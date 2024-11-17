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
	"log"
	"os"
	"regexp"
	"strconv"
	"strings"

	"cloud.google.com/go/firestore"
	"cloud.google.com/go/storage"
	"github.com/gocolly/colly"
	"github.com/gocolly/colly/debug"
	"google.golang.org/api/iterator"
)

// ScrapedDocument represents metadata about a scraped document
type ScrapedDocument struct {
	Filename    string `json:"filename"`
	URL         string `json:"url"`
	GCSPath     string `json:"gcs_path"`
	ContentType string `json:"content_type"`
}

// JobInput represents the input data for a scraping job
type JobInput struct {
	URL        string `json:"url"`
	EngineName string `json:"query_engine_name"`
	DepthLimit string `json:"depth_limit"`
}

// Add global storage client
var storageClient *storage.Client

func main() {
	ctx := context.Background()

	// Configure logger
	configureLogger()

	// Retrieve environment variables
	projectID, jobID := getEnvVariables()

	// Initialize Firestore client
	firestoreClient := initializeFirestore(ctx, projectID)
	defer firestoreClient.Close()

	// Initialize storage client
	var err error
	storageClient, err = storage.NewClient(ctx)
	if err != nil {
		log.Printf("Failed to create storage client: %v", err)
		os.Exit(1)
	}
	defer storageClient.Close()

	// Retrieve and parse job document
	jobDoc, docRef := fetchJobDocument(ctx, firestoreClient, jobID)
	jobInput := parseJobInput(ctx, jobDoc, docRef)

	// Generate and initialize bucket
	bucketName := generateAndInitializeBucket(ctx, projectID, jobInput, docRef)

	// Set up Colly collector
	collector, scrapedDocs := setupCollector(ctx, jobInput, bucketName, docRef)

	// Start scraping
	err = collector.Visit(jobInput.URL)
	if err != nil {
		log.Printf("Error starting scrape: %v", err)
	}
	collector.Wait()

	log.Printf("Scraping complete. Found %d documents", len(*scrapedDocs))

	// Save results and update job status
	saveResults(ctx, firestoreClient, docRef, scrapedDocs)
}

func configureLogger() {
	log.SetOutput(os.Stdout)
}

func getEnvVariables() (string, string) {
	projectID := os.Getenv("GCP_PROJECT")
	if projectID == "" {
		err := fmt.Errorf("GCP_PROJECT environment variable not set")
		log.Print(err)
		os.Exit(1)
	}

	jobID := os.Getenv("JOB_ID")
	if jobID == "" {
		err := fmt.Errorf("JOB_ID environment variable not set")
		log.Print(err)
		os.Exit(1)
	}
	log.Printf("Processing job ID: %s", jobID)

	return projectID, jobID
}

func initializeFirestore(ctx context.Context, projectID string) *firestore.Client {
	firestoreClient, err := firestore.NewClient(ctx, projectID)
	if err != nil {
		log.Printf("Failed to create Firestore client: %v", err)
		os.Exit(1)
	}
	return firestoreClient
}

func fetchJobDocument(ctx context.Context, firestoreClient *firestore.Client, jobID string) (*firestore.DocumentSnapshot, *firestore.DocumentRef) {
	collectionName := "batch_jobs"
	docRef := firestoreClient.Collection(collectionName).Doc(jobID)
	jobDoc, err := docRef.Get(ctx)
	if err != nil {
		updateJobError(ctx, docRef, fmt.Errorf("failed to get job document: %v", err))
		log.Print(err)
		return nil, docRef
	}
	return jobDoc, docRef
}

func parseJobInput(ctx context.Context, jobDoc *firestore.DocumentSnapshot, docRef *firestore.DocumentRef) JobInput {
	var jobInput JobInput
	inputData, ok := jobDoc.Data()["input_data"].(string)
	if !ok {
		err := fmt.Errorf("failed to get input_data as string from job document")
		updateJobError(ctx, docRef, err)
		log.Print(err)
		return jobInput
	}
	if err := json.Unmarshal([]byte(inputData), &jobInput); err != nil {
		updateJobError(ctx, docRef, fmt.Errorf("failed to decode job input: %v", err))
		log.Print(err)
		return jobInput
	}
	log.Printf("Job input: %+v", jobInput)

	// Validate job input
	if jobInput.URL == "" {
		err := fmt.Errorf("URL not found in input data")
		updateJobError(ctx, docRef, err)
		log.Print(err)
	}
	if jobInput.DepthLimit == "" {
		err := fmt.Errorf("depth limit not found in input data")
		updateJobError(ctx, docRef, err)
		log.Print(err)
	}
	_, err := strconv.Atoi(jobInput.DepthLimit)
	if err != nil {
		err := fmt.Errorf("invalid depth limit value %s", jobInput.DepthLimit)
		updateJobError(ctx, docRef, err)
		log.Print(err)
	}
	if jobInput.EngineName == "" {
		err := fmt.Errorf("query engine name not found in input data")
		updateJobError(ctx, docRef, err)
		log.Print(err)
	}

	return jobInput
}

func generateAndInitializeBucket(ctx context.Context, projectID string, jobInput JobInput, docRef *firestore.DocumentRef) string {
	// Generate bucket name
	bucketName, err := generateBucketName(projectID, jobInput.EngineName)
	if err != nil {
		updateJobError(ctx, docRef, err)
		log.Print(err)
	}

	log.Printf("Using bucket: %s", bucketName)

	// Initialize bucket
	if err := initializeBucket(ctx, projectID, bucketName); err != nil {
		updateJobError(ctx, docRef, fmt.Errorf("failed to initialize bucket: %v", err))
		log.Print(err)
	}

	return bucketName
}

func setupCollector(ctx context.Context, jobInput JobInput, bucketName string, docRef *firestore.DocumentRef) (*colly.Collector, *[]ScrapedDocument) {
	var scrapedDocs []ScrapedDocument

	baseDomain := extractDomain(jobInput.URL)
	allowedDomains := []string{
		baseDomain,
		"www." + baseDomain,
	}
	log.Printf("Allowed domains: %v", allowedDomains)

	// Create a new collector with debug logging
	c := colly.NewCollector(
		colly.MaxDepth(func() int {
			depth, err := strconv.Atoi(jobInput.DepthLimit)
			if err != nil {
				log.Printf("Invalid depth limit, defaulting to 1")
				return 1
			}
			return depth
		}()),
		colly.AllowedDomains(allowedDomains...), // Allow both with and without www
		colly.Debugger(&debug.LogDebugger{}),
		colly.Async(true),
		colly.UserAgent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"),
	)

	// Add error handling
	c.OnError(func(r *colly.Response, err error) {
		log.Printf("Error scraping %s: %v", r.Request.URL, err)
	})

	// Log when starting a new page
	c.OnRequest(func(r *colly.Request) {
		log.Printf("Visiting %s", r.URL.String())
	})

	// Handle all responses
	c.OnResponse(func(r *colly.Response) {
		handleResponse(r, bucketName, &scrapedDocs)
	})

	// Handle HTML elements
	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
		handleHTML(e)
	})

	return c, &scrapedDocs
}

func handleResponse(r *colly.Response, bucketName string, scrapedDocs *[]ScrapedDocument) {
	contentType := r.Headers.Get("Content-Type")
	log.Printf("Got response from %s (type: %s)", r.Request.URL, contentType)

	// Skip non-HTML, non-PDF content
	if !strings.Contains(contentType, "text/html") && !strings.Contains(contentType, "application/pdf") {
		log.Printf("Skipping non-HTML/PDF content type: %s", contentType)
		return
	}

	// Generate filename from URL
	filename := sanitizeFilename(r.Request.URL.String())
	if strings.Contains(contentType, "application/pdf") {
		if !strings.HasSuffix(filename, ".pdf") {
			filename += ".pdf"
		}
	} else {
		if !strings.HasSuffix(filename, ".html") {
			filename += ".html"
		}
	}

	// Create GCS path
	gcsPath := fmt.Sprintf("gs://%s/%s", bucketName, filename)
	log.Printf("Saving content to: %s", gcsPath)

	// Write content to GCS
	if err := writeDataToGCS(context.Background(), bucketName, filename, r.Body); err != nil {
		log.Printf("Error writing to GCS: %v", err)
		return
	}

	// Add to scraped documents
	doc := ScrapedDocument{
		URL:         r.Request.URL.String(),
		Filename:    filename,
		GCSPath:     gcsPath,
		ContentType: contentType,
	}
	*scrapedDocs = append(*scrapedDocs, doc)
	log.Printf("Successfully saved document: %s", gcsPath)
}

func handleHTML(e *colly.HTMLElement) {
	link := e.Attr("href")
	log.Printf("Found link: %s", link)

	// Handle relative URLs
	absoluteURL := e.Request.AbsoluteURL(link)
	if absoluteURL == "" {
		log.Printf("Skipping invalid URL: %s", link)
		return
	}

	if strings.HasSuffix(strings.ToLower(link), ".pdf") {
		log.Printf("Found PDF link: %s", absoluteURL)
		e.Request.Visit(absoluteURL)
	} else {
		// Visit all links within depth limit
		log.Printf("Visiting URL: %s", absoluteURL)
		e.Request.Visit(absoluteURL)
	}
}

func saveResults(ctx context.Context, firestoreClient *firestore.Client, docRef *firestore.DocumentRef, scrapedDocs *[]ScrapedDocument) {
	// Write results as JSON to stdout for job results
	if err := json.NewEncoder(os.Stdout).Encode(scrapedDocs); err != nil {
		updateJobError(ctx, docRef, fmt.Errorf("error encoding results: %v", err))
		log.Print(err)
		return
	}

	// Update the job document with results
	resultData := map[string]interface{}{
		"scraped_documents": scrapedDocs,
	}

	_, err := docRef.Update(ctx, []firestore.Update{
		{Path: "result_data", Value: resultData},
	})
	if err != nil {
		updateJobError(ctx, docRef, fmt.Errorf("failed to update job document: %v", err))
		log.Print(err)
		return
	}
	log.Printf("Successfully updated job with %d scraped documents", len(*scrapedDocs))

	// Update job status to succeeded
	_, err = docRef.Update(ctx, []firestore.Update{
		{Path: "status", Value: "succeeded"},
	})
	if err != nil {
		updateJobError(ctx, docRef, fmt.Errorf("failed to update job document status: %v", err))
		log.Print(err)
		return
	}
	log.Printf("Successfully updated job status")
}

// sanitizeFilename sanitizes the URL to create a safe filename
func sanitizeFilename(url string) string {
	// Remove the scheme and domain
	parts := strings.SplitN(url, "://", 2)
	if len(parts) == 2 {
		parts = strings.SplitN(parts[1], "/", 2)
		if len(parts) == 2 {
			url = parts[1]
		}
	}

	// Replace invalid characters
	safe := strings.Map(func(r rune) rune {
		if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') || (r >= '0' && r <= '9') || r == '-' || r == '_' || r == '.' {
			return r
		}
		return '_'
	}, url)

	// Truncate if too long
	if len(safe) > 200 {
		safe = safe[:200]
	}

	return safe
}

// extractDomain extracts the base domain from a URL
func extractDomain(url string) string {
	domain := ""
	parts := strings.SplitN(url, "://", 2)
	if len(parts) == 2 {
		// Get the domain part
		domain = strings.SplitN(parts[1], "/", 2)[0]

		// Handle www and other subdomains
		domain = strings.TrimPrefix(domain, "www.")
	}
	log.Printf("Extracted domain: %s from URL: %s", domain, url)
	return domain
}

// generateBucketName generates a GCS bucket name based on project ID and engine name
func generateBucketName(projectID string, qEngineName string) (string, error) {
	// Replace spaces and underscores with hyphens, convert to lowercase
	qeName := strings.ToLower(qEngineName)
	qeName = strings.ReplaceAll(qeName, " ", "-")
	qeName = strings.ReplaceAll(qeName, "_", "-")

	bucketName := fmt.Sprintf("%s-downloads-%s", projectID, qeName)

	// Validate bucket name matches GCS requirements
	if match, _ := regexp.MatchString("^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$", bucketName); !match {
		return "", fmt.Errorf("invalid bucket name: %s", bucketName)
	}

	return bucketName, nil
}

// initializeBucket initializes the GCS bucket by creating it if it doesn't exist
// or clearing its contents if it does
func initializeBucket(ctx context.Context, projectID, bucketName string) error {
	bucket := storageClient.Bucket(bucketName)

	// Check if bucket exists
	_, err := bucket.Attrs(ctx)
	if err == storage.ErrBucketNotExist {
		log.Printf("Creating bucket %s", bucketName)
		if err := bucket.Create(ctx, projectID, nil); err != nil {
			return fmt.Errorf("error creating bucket: %v", err)
		}
	} else if err != nil {
		return fmt.Errorf("error checking bucket: %v", err)
	} else {
		// Bucket exists, clear all objects
		log.Printf("Clearing existing objects from bucket %s", bucketName)
		it := bucket.Objects(ctx, nil)
		for {
			attrs, err := it.Next()
			if err == iterator.Done {
				break
			}
			if err != nil {
				return fmt.Errorf("error listing objects: %v", err)
			}
			if err := bucket.Object(attrs.Name).Delete(ctx); err != nil {
				return fmt.Errorf("error deleting object %s: %v", attrs.Name, err)
			}
		}
	}
	return nil
}

// writeDataToGCS writes data to the specified GCS bucket and filename
func writeDataToGCS(ctx context.Context, bucketName string, filename string, content []byte) error {
	// Use global storage client instead of creating new one
	bucket := storageClient.Bucket(bucketName)

	// Write content to GCS
	obj := bucket.Object(filename)
	writer := obj.NewWriter(ctx)

	if _, err := writer.Write(content); err != nil {
		return fmt.Errorf("error writing to GCS: %v", err)
	}

	if err := writer.Close(); err != nil {
		return fmt.Errorf("error closing GCS writer: %v", err)
	}

	log.Printf("Successfully wrote %s to GCS bucket %s", filename, bucketName)
	return nil
}

// updateJobError updates the job document with the provided error and sets status to failed
func updateJobError(ctx context.Context, docRef *firestore.DocumentRef, err error) {
	_, updateErr := docRef.Update(ctx, []firestore.Update{
		{Path: "errors", Value: []string{err.Error()}},
		{Path: "status", Value: "failed"},
	})
	if updateErr != nil {
		log.Printf("Failed to update job error status: %v", updateErr)
	}
}
