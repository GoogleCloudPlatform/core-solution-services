package main

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"os"
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
	content []byte
}

func (w *mockWriter) Write(p []byte) (n int, err error) {
	w.content = append(w.content, p...)
	return len(p), nil
}

func (w *mockWriter) Close() error {
	return nil
}

func (w *mockWriter) Attrs() *storage.ObjectAttrs {
	return &storage.ObjectAttrs{}
}

type mockObject struct {
	name    string
	content []byte
}

func (o *mockObject) NewWriter(ctx context.Context) io.WriteCloser {
	return &mockWriter{content: make([]byte, 0)}
}

func (o *mockObject) Delete(ctx context.Context) error {
	return nil
}

type mockBucket struct {
	name    string
	objects map[string]*mockObject
}

func (b *mockBucket) Object(name string) interface {
	NewWriter(context.Context) io.WriteCloser
	Delete(context.Context) error
} {
	if obj, exists := b.objects[name]; exists {
		return obj
	}
	obj := &mockObject{name: name}
	b.objects[name] = obj
	return obj
}

func (b *mockBucket) Create(ctx context.Context, projectID string, attrs *storage.BucketAttrs) error {
	return nil
}

func (b *mockBucket) Attrs(ctx context.Context) (*storage.BucketAttrs, error) {
	return &storage.BucketAttrs{}, nil
}

func (b *mockBucket) Objects(ctx context.Context, q *storage.Query) *storage.ObjectIterator {
	return &storage.ObjectIterator{}
}

type mockStorage struct {
	buckets map[string]*mockBucket
}

func (s *mockStorage) Bucket(name string) interface {
	Object(string) interface {
		NewWriter(context.Context) io.WriteCloser
		Delete(context.Context) error
	}
	Create(context.Context, string, *storage.BucketAttrs) error
	Attrs(context.Context) (*storage.BucketAttrs, error)
	Objects(context.Context, *storage.Query) *storage.ObjectIterator
} {
	if bucket, exists := s.buckets[name]; exists {
		return bucket
	}
	bucket := &mockBucket{
		name:    name,
		objects: make(map[string]*mockObject),
	}
	s.buckets[name] = bucket
	return bucket
}

func (s *mockStorage) Close() error {
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
	mockClient := &mockStorage{
		buckets: make(map[string]*mockBucket),
	}
	storageClient = mockClient

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
