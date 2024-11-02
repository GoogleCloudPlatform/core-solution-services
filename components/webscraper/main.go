package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"strconv"
	"strings"

	"cloud.google.com/go/storage"
	"github.com/gocolly/colly"
	"github.com/gocolly/colly/debug"
)

// ScrapedDocument represents metadata about a scraped document
type ScrapedDocument struct {
	Filename    string `json:"filename"`
	URL         string `json:"url"`
	GCSPath     string `json:"gcs_path"`
	ContentType string `json:"content_type"`
}

func main() {
	// Configure logger to write to stdout
	log.SetOutput(os.Stdout)

	// Get environment variables
	url := os.Getenv("URL")
	if url == "" {
		log.Fatal("URL environment variable not set")
	}
	log.Printf("Starting scrape of URL: %s", url)

	depthLimitStr := os.Getenv("DEPTH_LIMIT")
	if depthLimitStr == "" {
		log.Fatal("DEPTH_LIMIT environment variable not set")
	}
	depthLimit, err := strconv.Atoi(depthLimitStr)
	if err != nil {
		log.Fatal("Invalid DEPTH_LIMIT value")
	}
	log.Printf("Depth limit set to: %d", depthLimit)

	projectID := os.Getenv("GCP_PROJECT")
	if projectID == "" {
		log.Fatal("GCP_PROJECT environment variable not set")
	}

	// Generate bucket name
	bucketName := fmt.Sprintf("%s-downloads-%s", projectID,
		strings.ReplaceAll(strings.ReplaceAll(url, "://", "-"), "/", "-"))
	log.Printf("Using bucket: %s", bucketName)

	// Create a slice to store document metadata
	var scrapedDocs []ScrapedDocument

	baseDomain := extractDomain(url)
	allowedDomains := []string{
		baseDomain,
		"www." + baseDomain,
	}
	log.Printf("Allowed domains: %v", allowedDomains)

	// Create a new collector with debug logging
	c := colly.NewCollector(
		colly.MaxDepth(depthLimit),
		colly.AllowedDomains(allowedDomains...), // Allow both with and without www
		colly.Debugger(&debug.LogDebugger{}),
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
		contentType := r.Headers.Get("Content-Type")
		log.Printf("Got response from %s (type: %s)", r.Request.URL, contentType)

		// Generate filename from URL
		filename := sanitizeFilename(r.Request.URL.String())
		if !strings.HasSuffix(filename, ".html") && !strings.HasSuffix(filename, ".pdf") {
			filename += ".html"
		}

		// Create GCS path
		gcsPath := fmt.Sprintf("gs://%s/%s", bucketName, filename)

		// Write content to GCS
		err := writeDataToGCS(bucketName, filename, r.Body)
		if err != nil {
			log.Printf("Error writing to GCS: %v\n", err)
			return
		}

		// Store document metadata
		doc := ScrapedDocument{
			Filename:    filename,
			URL:         r.Request.URL.String(),
			GCSPath:     gcsPath,
			ContentType: contentType,
		}
		scrapedDocs = append(scrapedDocs, doc)
		log.Printf("Scraped document: %+v\n", doc)
	})

	// Add PDF link detection and handle all links
	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
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
			e.Request.Visit(absoluteURL)
		}
	})

	// Start scraping
	log.Printf("Starting scrape...")
	err = c.Visit(url)
	if err != nil {
		log.Printf("Error starting scrape: %v", err)
	}

	// Wait for scraping to finish
	c.Wait()

	log.Printf("Scraping complete. Found %d documents", len(scrapedDocs))

	// Write results as JSON to stdout for job results
	if err := json.NewEncoder(os.Stdout).Encode(scrapedDocs); err != nil {
		log.Printf("Error encoding results: %v", err)
	}
}

func writeDataToGCS(bucketName, objectName string, data []byte) error {
	ctx := context.Background()
	client, err := storage.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("storage.NewClient: %w", err)
	}
	defer client.Close()

	bucket := client.Bucket(bucketName)

	// Create bucket if it doesn't exist
	if err := bucket.Create(ctx, "", nil); err != nil {
		// Ignore error if bucket already exists
		if !strings.Contains(err.Error(), "already exists") {
			return fmt.Errorf("Bucket.Create: %w", err)
		}
	}

	obj := bucket.Object(objectName)
	w := obj.NewWriter(ctx)

	if _, err := w.Write(data); err != nil {
		return fmt.Errorf("Writer.Write: %w", err)
	}

	if err := w.Close(); err != nil {
		return fmt.Errorf("Writer.Close: %w", err)
	}

	return nil
}

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

func extractDomain(url string) string {
	domain := ""
	parts := strings.SplitN(url, "://", 2)
	if len(parts) == 2 {
		// Get the domain part
		domain = strings.SplitN(parts[1], "/", 2)[0]

		// Handle www and other subdomains
		if strings.HasPrefix(domain, "www.") {
			domain = domain[4:] // Remove www.
		}
	}
	log.Printf("Extracted domain: %s from URL: %s", domain, url)
	return domain
}
