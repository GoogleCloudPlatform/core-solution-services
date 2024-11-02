"""Web data source that uses batch jobs for scraping"""

import os
from typing import List
from google.cloud import storage
from common.utils.kf_job_app import kube_create_job
from common.models.batch_job import BatchJobModel
from services.query.data_source import DataSource, DataSourceFile
from common.utils.logging_handler import Logger
from config import PROJECT_ID, JOB_TYPE_WEBSCRAPER

Logger = Logger.get_logger(__file__)

class WebDataSourceJob(DataSource):
  """Web site data source that uses batch jobs for scraping"""

  def __init__(self, storage_client, query_engine_name: str, params=None):
    """Initialize the WebDataSourceJob
    
    Args:
        storage_client: Google cloud storage client instance
        query_engine_name: Name of the query engine
        params: Optional parameters dict
    """
    super().__init__(storage_client, params)
    self.namespace = os.getenv("SKAFFOLD_NAMESPACE", "default")
    self.query_engine_name = query_engine_name

  def download_documents(self, doc_url: str, temp_dir: str) -> List[DataSourceFile]:
    """Start webscraper job to download files from doc_url
    
    Args:
        doc_url: URL to scrape
        temp_dir: Path to temporary directory (not used for job-based scraping)
        
    Returns:
        List of DataSourceFile objects representing scraped pages
    """
    Logger.info(f"Starting webscraper job for URL: {doc_url}")

    # Create job spec
    job_input = {
      "url": doc_url,
      "title": f"webscraper-{doc_url.replace('://', '-').replace('/', '-')}",
      "depth_limit": self.depth_limit,
      "query_engine_name": self.query_engine_name
    }

    job_specs = {
      "type": JOB_TYPE_WEBSCRAPER,
      "input_data": job_input,
      "container_image": f"gcr.io/{PROJECT_ID}/webscraper:latest"
    }

    # Set environment variables. Depth limit for scraper is GENIE depth+1
    env_vars = {
      "GCP_PROJECT": PROJECT_ID,
      "URL": doc_url,
      "DEPTH_LIMIT": str(self.depth_limit + 1)
    }

    # Create and start the job
    job_model = kube_create_job(
      job_specs=job_specs,
      namespace=self.namespace, 
      env_vars=env_vars
    )

    Logger.info(f"Started webscraper job {job_model.id}")

    # Wait for job completion and get results
    job_model = BatchJobModel.find_by_id(job_model.id)
    while job_model.status not in ["completed", "failed"]:
      job_model = BatchJobModel.find_by_id(job_model.id)

    if job_model.status == "failed":
      raise Exception(f"Webscraper job failed: {job_model.error}")

    # Convert job results to DataSourceFile objects
    doc_files = []
    for result in job_model.results:
      doc_file = DataSourceFile(
        doc_name=result["filename"],
        src_url=result["url"], 
        gcs_path=result["gcs_path"],
        mime_type=result["content_type"]
      )
      doc_files.append(doc_file)

    Logger.info(f"Webscraper job completed with {len(doc_files)} files")
    return doc_files 