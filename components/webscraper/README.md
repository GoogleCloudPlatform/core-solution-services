# Webscraper Component

The webscraper component provides web crawling and content extraction capabilities for GENIE's Query Engine system. It crawls websites to a specified depth and extracts both HTML and PDF content, storing the results in Google Cloud Storage for later processing by the LLM service.

## Technical Approach

The webscraper consists of two main subcomponents:

1. A Go-based web crawler (`main.go`) built using the [Colly](http://go-colly.org/) framework that performs the actual crawling
2. A Python wrapper (`scrape_url.py`) that provides a command-line interface for testing and direct use

The scraper is typically launched as a Kubernetes job during Query Engine builds via the `WebDataSourceJob` class, but can also be run directly using the command-line script.

Key features:
- Crawls websites to a configurable depth
- Extracts both HTML and PDF content
- Stores content in GCS buckets organized by query engine name
- Records metadata about scraped documents in Firestore
- Integrates with the batch job system for tracking progress and results

## Build and Deploy

### Build the container

From the root of the repository:

```bash
skaffold build -m webscraper
```

This will build and push the container to your project's container registry.

## Running Tests

The webscraper includes integration tests that use the Firebase emulator and GCS emulator. To run the tests:

```bash
cd components/webscraper
./run_tests.sh
```

The test script will:
1. Install required dependencies if needed
2. Start the Firebase and GCS emulators
3. Run the Go tests with the emulators

## Command Line Usage

While the webscraper is typically used as part of the Query Engine build process, it can also be run directly using the `scrape_url.py` script for testing or one-off scraping jobs.

### Prerequisites

Set your PYTHONPATH to include the common package:

```bash
export PYTHONPATH=../common/src
```

### Basic Usage

```bash
python scrape_url.py <url>
```

### Options

```bash
python scrape_url.py [--depth DEPTH] [--engine ENGINE_NAME] <url>

Arguments:
  url                   URL to scrape
  --depth DEPTH         Maximum depth to crawl (default: 1) 
  --engine ENGINE_NAME  Query engine name (default: default)
```

### Example

```bash
python scrape_url.py --depth 2 --engine my-engine https://example.com
```

This will:
1. Create a batch job to track the scraping process
2. Launch the webscraper container to crawl example.com
3. Store the results in a GCS bucket named `<project-id>-downloads-my-engine`
4. Update the batch job with results and status

The scraped content can then be used to build a query engine in the LLM service.

## Output

The script outputs:
- Number of pages scraped
- GCS bucket location
- List of scraped URLs
- List of downloaded files in GCS

Example output:
```
Created job with ID: 12345-abcd

Scraped 3 pages:

GCS Bucket: gs://my-project-downloads-my-engine

Scraped URLs:
- https://example.com
- https://example.com/page1
- https://example.com/doc.pdf

Downloaded files:
- gs://my-project-downloads-my-engine/index.html
- gs://my-project-downloads-my-engine/page1.html 
- gs://my-project-downloads-my-engine/doc.pdf
```

## Integration with Query Engines

The webscraper is integrated into the Query Engine build process through the `WebDataSourceJob` class. When building a Query Engine with a web URL as the data source, the system will:

1. Create a batch job for the scraping process
2. Launch the webscraper as a Kubernetes job
3. Monitor the job for completion
4. Process the scraped documents into the Query Engine's vector store

The depth of crawling can be configured through the Query Engine build parameters:
```python
params = {
    "depth_limit": "2"  # Crawl up to 2 levels deep
}
```