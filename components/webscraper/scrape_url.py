#!/usr/bin/env python3

import argparse
import json
import os
import subprocess
import sys
import uuid

try:
    from common.models.batch_job import BatchJobModel, JobStatus
except ImportError:
    print("Error: Unable to import common package.")
    print("Usage: PYTHONPATH=../common/src python scrape_url.py <your url>")
    print("\nMake sure you've set your PYTHONPATH to include the common package location.")
    print("\nAlso make sure to run in a virtual environment with fireo and other packages from common/requirements.txt installed.")
    sys.exit(1)

def get_gcp_project():
    """Get GCP project from gcloud config"""
    result = subprocess.run(
        ['gcloud', 'config', 'get', 'project'],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def create_batch_job(url: str, depth_limit: str, engine_name: str) -> BatchJobModel:
    """Create a new batch job for the webscraper"""
    job_input = {
        "url": url,
        "depth_limit": str(depth_limit),
        "query_engine_name": engine_name
    }
    
    job = BatchJobModel()
    job.id = str(uuid.uuid4())
    job.uuid = job.id
    job.name = f"webscraper-{job.id[:8]}"
    job.type = "webscraper"
    job.status = JobStatus.JOB_STATUS_PENDING.value
    job.input_data = json.dumps(job_input)
    job.save()
    
    return job

def run_webscraper(job_id: str, project_id: str):
    """Run the webscraper with the given job ID"""
    env = os.environ.copy()
    env["GCP_PROJECT"] = project_id
    env["JOB_ID"] = job_id
    
    result = subprocess.run(
        ['go', 'run', 'main.go'],
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error running webscraper: {result.stderr}")
        return False
    
    return True

def main():
    parser = argparse.ArgumentParser(
        description='Scrape a URL using the webscraper',
        epilog='Example usage: PYTHONPATH=../common/src python scrape_url.py <your url>'
    )
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('--depth', type=str, default="1", help='Depth limit for scraping')
    parser.add_argument('--engine', type=str, default="default", help='Query engine name')
    args = parser.parse_args()

    # Get GCP project
    project_id = get_gcp_project()
    if not project_id:
        print("Error: Could not determine GCP project")
        return

    # Create batch job
    job = create_batch_job(args.url, args.depth, args.engine)
    print(f"Created job with ID: {job.id}")

    # Run webscraper
    success = run_webscraper(job.id, project_id)
    if not success:
        print("Webscraper failed")
        return

    # Fetch updated job to get results
    job = BatchJobModel.find_by_uuid(job.id)
    if job.status != JobStatus.JOB_STATUS_SUCCEEDED.value:
        print(f"Job failed with status: {job.status}")
        if job.errors:
            print(f"Errors: {job.errors}")
        return

    # Extract and display results
    if job.result_data and 'scraped_documents' in job.result_data:
        docs = job.result_data['scraped_documents']
        if docs is None:
            print(f"\nScraped 0 pages")
        else:
            print(f"\nScraped {len(docs)} pages:")
            
            gcs_path = docs[0]['GCSPath']
            bucket_name = gcs_path.split('/')[2]
            print(f"\nGCS Bucket: gs://{bucket_name}")
            
            # Print all URLs and their corresponding GCS paths
            print("\nScraped URLs:")
            for doc in docs:
                print(f"- {doc['URL']}")
                
            print("\nDownloaded files:")
            for doc in docs:
                print(f"- {doc['GCSPath']}")
    
if __name__ == "__main__":
    main() 