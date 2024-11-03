package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"strings"
	"testing"
	"time"

	"cloud.google.com/go/firestore"
	"cloud.google.com/go/storage"
	"github.com/stretchr/testify/assert"
)

// Helper function to clear Firestore
func clearFirestore(t *testing.T) {
	req, err := http.NewRequest("DELETE",
		"http://localhost:8080/emulator/v1/projects/fake-project/databases/(default)/documents",
		nil)
	if err != nil {
		t.Fatalf("Failed to create request: %v", err)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		t.Fatalf("Failed to clear Firestore: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		t.Fatalf("Failed to clear Firestore, status: %d", resp.StatusCode)
	}
}

// Mock GCS storage client components
type mockWriter struct {
	strings.Builder
}

func (w *mockWriter) Write(p []byte) (n int, err error) {
	return w.Builder.Write(p)
}

func (w *mockWriter) Close() error {
	return nil
}

type mockObjectHandle struct {
	name    string
	content string
	writer  *mockWriter
}

func (o *mockObjectHandle) NewWriter(ctx context.Context) *storage.Writer {
	o.writer = &mockWriter{}
	return &storage.Writer{}
}

func (o *mockObjectHandle) Delete(ctx context.Context) error {
	return nil
}

type mockBucketHandle struct {
	objects map[string]*mockObjectHandle
}

func (b *mockBucketHandle) Object(name string) *storage.ObjectHandle {
	if _, exists := b.objects[name]; !exists {
		b.objects[name] = &mockObjectHandle{name: name}
	}
	return &storage.ObjectHandle{}
}

func (b *mockBucketHandle) Create(ctx context.Context, projectID string, attrs *storage.BucketAttrs) error {
	return nil
}

func (b *mockBucketHandle) Attrs(ctx context.Context) (*storage.BucketAttrs, error) {
	return nil, storage.ErrBucketNotExist
}

func (b *mockBucketHandle) Objects(ctx context.Context, q *storage.Query) *storage.ObjectIterator {
	return &storage.ObjectIterator{}
}

// Create interface for storage client to ensure our mock matches required methods
type storageClientInterface interface {
	Bucket(name string) *storage.BucketHandle
	Close() error
}

// Mock storage client
type mockStorageClient struct {
	buckets map[string]*mockBucketHandle
}

func (c *mockStorageClient) Bucket(name string) *storage.BucketHandle {
	if _, exists := c.buckets[name]; !exists {
		c.buckets[name] = &mockBucketHandle{
			objects: make(map[string]*mockObjectHandle),
		}
	}
	return &storage.BucketHandle{}
}

func (c *mockStorageClient) Close() error {
	return nil
}

func TestWebscraper(t *testing.T) {
	// Clear Firestore before test
	clearFirestore(t)

	// Setup test server with mock website
	ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/":
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprintf(w, `
				<html>
					<body>
						<a href="/page1.html">Page 1</a>
						<a href="/document.pdf">Sample PDF</a>
					</body>
				</html>
			`)
		case "/page1.html":
			w.Header().Set("Content-Type", "text/html")
			fmt.Fprintf(w, `
				<html>
					<body>
						<h1>Page 1</h1>
						<p>Test content</p>
					</body>
				</html>
			`)
		case "/document.pdf":
			w.Header().Set("Content-Type", "application/pdf")
			fmt.Fprintf(w, "Mock PDF content")
		}
	}))
	defer ts.Close()

	// Setup environment variables
	os.Setenv("GCP_PROJECT", "fake-project")
	jobID := fmt.Sprintf("test-job-%d", time.Now().Unix())
	os.Setenv("JOB_ID", jobID)

	// Initialize Firestore client
	os.Setenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")
	ctx := context.Background()
	client, err := firestore.NewClient(ctx, "fake-project")
	if err != nil {
		t.Fatalf("Failed to create Firestore client: %v", err)
	}
	defer client.Close()

	// Initialize mock storage client
	mockClient := &storage.Client{}
	storageClient = mockClient // Set the global storage client to our mock

	// Create test batch job
	jobInput := JobInput{
		URL:        ts.URL,
		EngineName: "test-engine",
		DepthLimit: "2",
	}
	inputJSON, err := json.Marshal(jobInput)
	if err != nil {
		t.Fatalf("Failed to marshal job input: %v", err)
	}

	_, err = client.Collection("batch_jobs").Doc(jobID).Set(ctx, map[string]interface{}{
		"id":          jobID,
		"name":        "Test Webscraper Job",
		"type":        "webscraper",
		"status":      "active",
		"input_data":  string(inputJSON),
		"message":     "",
		"errors":      map[string]interface{}{},
		"job_logs":    map[string]interface{}{},
		"metadata":    map[string]interface{}{},
		"result_data": map[string]interface{}{},
	})
	if err != nil {
		t.Fatalf("Failed to create test job: %v", err)
	}

	// Run the webscraper
	main()

	// Verify results in Firestore
	doc, err := client.Collection("batch_jobs").Doc(jobID).Get(ctx)
	if err != nil {
		t.Fatalf("Failed to get job document: %v", err)
	}

	resultData, ok := doc.Data()["result_data"].(map[string]interface{})
	assert.True(t, ok, "Result data should be a map")

	scrapedDocs, ok := resultData["scraped_documents"].([]interface{})
	assert.True(t, ok, "Scraped documents should be an array")
	assert.Equal(t, 3, len(scrapedDocs), "Should have scraped 3 documents")

	// Verify each scraped document
	foundHTML := false
	foundPDF := false
	for _, doc := range scrapedDocs {
		docMap := doc.(map[string]interface{})
		contentType := docMap["content_type"].(string)
		if contentType == "text/html" {
			foundHTML = true
		} else if contentType == "application/pdf" {
			foundPDF = true
		}
	}

	assert.True(t, foundHTML, "Should have found HTML documents")
	assert.True(t, foundPDF, "Should have found PDF document")
}
