package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"
	"time"

	"cloud.google.com/go/firestore"
	"cloud.google.com/go/storage"
	"github.com/stretchr/testify/assert"
	"google.golang.org/api/option"
)

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
	os.Setenv("STORAGE_EMULATOR_HOST", "localhost:9199")
	jobID := fmt.Sprintf("test-job-%d", time.Now().Unix())
	os.Setenv("JOB_ID", jobID)

	// Initialize Firestore client (assumes emulator is running)
	os.Setenv("FIRESTORE_EMULATOR_HOST", "localhost:8080")
	ctx := context.Background()
	client, err := firestore.NewClient(ctx, "fake-project")
	if err != nil {
		t.Fatalf("Failed to create Firestore client: %v", err)
	}
	defer client.Close()

	// Initialize real storage client pointing to emulator
	storageClient, err := storage.NewClient(ctx, option.WithoutAuthentication())
	if err != nil {
		t.Fatalf("Failed to create storage client: %v", err)
	}
	defer storageClient.Close()

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
