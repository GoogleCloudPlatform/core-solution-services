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

	depthLimitStr := os.Getenv("DEPTH_LIMIT")
	if depthLimitStr == "" {
		log.Fatal("DEPTH_LIMIT environment variable not set")
	}
	depthLimit, err := strconv.Atoi(depthLimitStr)
	if err != nil {
		log.Fatal("Invalid DEPTH_LIMIT value")
	}

	projectID := os.Getenv("GCP_PROJECT")
	if projectID == "" {
		panic("GCP_PROJECT environment variable not set")
	}

	// Generate bucket name using same logic as WebDataSource class
	bucketName := fmt.Sprintf("%s-downloads-%s", projectID,
		strings.ReplaceAll(strings.ReplaceAll(url, "://", "-"), "/", "-"))

	// Create a slice to store document metadata
	var scrapedDocs []ScrapedDocument

	// Create a new collector
	c := colly.NewCollector(
		colly.MaxDepth(depthLimit),
		colly.AllowedDomains(extractDomain(url)), // Restrict to same domain
	)

	// Handle all responses
	c.OnResponse(func(r *colly.Response) {
		contentType := r.Headers.Get("Content-Type")

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

	// Add PDF link detection
	c.OnHTML("a[href]", func(e *colly.HTMLElement) {
		link := e.Attr("href")
		if strings.HasSuffix(strings.ToLower(link), ".pdf") {
			e.Request.Visit(link)
		}
	})

	// Start scraping
	c.Visit(url)

	// Write results as JSON to stdout for job results
	json.NewEncoder(os.Stdout).Encode(scrapedDocs)
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
	parts := strings.SplitN(url, "://", 2)
	if len(parts) != 2 {
		return ""
	}
	domain := strings.SplitN(parts[1], "/", 2)[0]
	return domain
}
