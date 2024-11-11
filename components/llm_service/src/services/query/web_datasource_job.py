"""Web data source that uses batch jobs for scraping"""

import json
import os
import time
import uuid
from typing import List
from timeout_decorator import timeout
from common.models.batch_job import BatchJobModel
from common.utils.config import JOB_TYPE_WEBSCRAPER
from common.utils.http_exceptions import InternalServerError
from common.utils.kf_job_app import (kube_create_job,
                                     get_latest_artifact_registry_image)
from common.utils.logging_handler import Logger
from services.query.data_source import DataSource, DataSourceFile
from config import PROJECT_ID

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
    if "depth_limit" in params:
      self.depth_limit = int(params["depth_limit"])
    else:
      self.depth_limit = 1

  def download_documents(self, doc_url: str, temp_dir: str) -> \
      List[DataSourceFile]:
    """Start webscraper job to download files from doc_url

    Args:
        doc_url: URL to scrape
        temp_dir: Path to temporary directory

    Returns:
        List of DataSourceFile objects representing scraped pages
    """
    Logger.info(f"Starting webscraper job for URL: {doc_url}")

    # create batch job model first
    job_model = BatchJobModel()
    job_model.id = str(uuid.uuid4())
    job_model.type = JOB_TYPE_WEBSCRAPER
    job_model.status = "pending"
    job_model.uuid = job_model.id
    job_model.name = f"webscraper-{job_model.id[:8]}"
    job_model.save()

    # create job input data with URL, job ID and engine name
    # depth limit for scraper is GENIE depth+1
    job_input = {
      "url": doc_url,
      "query_engine_name": self.query_engine_name,
      "depth_limit": str(self.depth_limit + 1),
    }

    # Get container image from Artifact Registry instead of deployment
    container_image = get_latest_artifact_registry_image(
        repository="default",
        package_name="webscraper",
        project_id=PROJECT_ID
    )

    job_specs = {
      "type": JOB_TYPE_WEBSCRAPER,
      "input_data": json.dumps(job_input),
      "container_image": container_image
    }

    # set environment variables.
    env_vars = {
      "GCP_PROJECT": PROJECT_ID,
      "JOB_ID": job_model.id
    }

    # create and start the job with existing job model
    kube_create_job(
      job_specs=job_specs,
      namespace=self.namespace,
      env_vars=env_vars,
      existing_job_model=job_model
    )

    Logger.info(f"Started webscraper job {job_model.id}")

    # wait for job completion and get results
    @timeout(6000)
    def wait_for_job(job_model):
      job_model = BatchJobModel.find_by_uuid(job_model.id)
      while job_model.status not in ["succeeded", "failed"]:
        time.sleep(1)
        job_model = BatchJobModel.find_by_uuid(job_model.id)
        Logger.info(f"Webscraper job {job_model.id} status {job_model.status}")

    try:
      wait_for_job(job_model)
    except Exception as e:
      raise InternalServerError("Timed out waiting for webscraper") from e
    if job_model.status != "succeeded":
      if job_model.status == "active":
        raise InternalServerError("Webscraper job failed to complete")
      else:
        raise InternalServerError(f"Webscraper job failed: {job_model.errors}")

    Logger.info(f"Webscraper job [{job_model.id}] completed")

    # Update result processing to match new schema
    doc_files = []
    if job_model.result_data and "scraped_documents" in job_model.result_data:
      scraped_docs = job_model.result_data["scraped_documents"]
      Logger.info(f"downloading [{len(scraped_docs)}] documents")
      for doc in scraped_docs:
        # Parse GCS path to get bucket and blob path
        gcs_path = doc["GCSPath"]
        if gcs_path.startswith("gs://"):
          bucket_name = gcs_path.split("/")[2]
          blob_path = "/".join(gcs_path.split("/")[3:])
        else:
          raise InternalServerError(f"Invalid GCS path format: {gcs_path}")

        # Download file from GCS
        blob = self.storage_client.get_bucket(bucket_name).blob(blob_path)
        local_path = os.path.join(temp_dir, doc["Filename"])
        blob.download_to_filename(local_path)

        doc_file = DataSourceFile(
            doc_name=doc["Filename"],
            src_url=doc["URL"],
            gcs_path=doc["GCSPath"],
            mime_type=doc["ContentType"],
            local_path=local_path
        )
        doc_files.append(doc_file)

    Logger.info(f"Webscraper job completed with {len(doc_files)} files")
    return doc_files
