package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"os"
	"path"
	"strconv"
	"strings"

	"cloud.google.com/go/storage"
	"github.com/gocolly/colly"
)

func main() {
	// Get environment variables
	url := os.Getenv("TARGET_URL")
	if url == "" {
		panic("TARGET_URL environment variable not set")
	}

	depthLimitStr := os.Getenv("DEPTH_LIMIT")
	if depthLimitStr == "" {
		panic("DEPTH_LIMIT environment variable not set")
	}
	depthLimit, err := strconv.Atoi(depthLimitStr)
	if err != nil {
		panic("Invalid DEPTH_LIMIT value")
	}

	gcsPath := os.Getenv("GCS_PATH")
	if gcsPath == "" {
		panic("GCS_PATH environment variable not set")
	}

	// Create a new collector
	c := colly.NewCollector(
		colly.MaxDepth(depthLimit), // Set depth limit
	)

	// Handle PDF files
	c.OnResponse(func(r *colly.Response) {
		contentType := r.Headers.Get("Content-Type")
		if strings.Contains(contentType, "application/pdf") {
			// Generate filename from URL
			fileName := path.Base(r.Request.URL.Path)
			if fileName == "" || fileName == "/" {
				fileName = "download.pdf"
			}

			// Create GCS path for PDF
			pdfPath := path.Join(path.Dir(gcsPath), fileName)

			// Write PDF content to GCS
			err := writeDataToGCS(pdfPath, string(r.Body))
			if err != nil {
				log.Printf("Error writing PDF to GCS: %v\n", err)
			} else {
				log.Printf("PDF uploaded to GCS: %s\n", pdfPath)
			}
		}
	})

	// Callback for when a scraped element is found
	c.OnHTML("title", func(e *colly.HTMLElement) {
		// Write scraped content to GCS
		err := writeDataToGCS(gcsPath, e.Text)
		if err != nil {
			log.Printf("Error writing to GCS: %v\n", err)
		} else {
			log.Printf("Scraped data uploaded to GCS: %s\n", gcsPath)
		}
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
}

func writeDataToGCS(gcsPath, data string) error {

	// Creates a client.
	ctx := context.Background()
	client, err := storage.NewClient(ctx)
	if err != nil {
		return fmt.Errorf("storage.NewClient: %w", err)
	}
	defer client.Close()

	// Creates a Writer.
	bucketName, objectName := parseGCSPath(gcsPath)
	wc := client.Bucket(bucketName).Object(objectName).NewWriter(ctx)
	if _, err = io.WriteString(wc, data); err != nil {
		return fmt.Errorf("io.WriteString: %w", err)
	}
	if err := wc.Close(); err != nil {
		return fmt.Errorf("Writer.Close: %w", err)
	}

	return nil
}

func parseGCSPath(gcsPath string) (string, string) {
	// Example: gs://my-bucket/path/to/file.txt
	// Returns: my-bucket, path/to/file.txt
	parts := strings.SplitN(gcsPath, "/", 4)
	if len(parts) == 4 {
		return parts[2], parts[3]
	}
	return "", ""
}
