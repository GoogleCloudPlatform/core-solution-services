// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

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
	os.Setenv("STORAGE_EMULATOR_HOST", "http://localhost:9023")
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
		contentType, ok := docMap["ContentType"].(string)
		if !ok {
			t.Fatalf("ContentType not found or not a string in document: %v", docMap)
		}
		if contentType == "text/html" {
			foundHTML = true
		} else if contentType == "application/pdf" {
			foundPDF = true
		}
	}

	assert.True(t, foundHTML, "Should have found HTML documents")
	assert.True(t, foundPDF, "Should have found PDF document")
}
