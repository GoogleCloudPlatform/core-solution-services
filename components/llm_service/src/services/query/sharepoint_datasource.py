# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Sharepoint DataSources
"""
import os
import re
from typing import List
from pathlib import Path
from common.utils.logging_handler import Logger
from common.models import QueryEngine
from config import (PROJECT_ID,
                    ONEDRIVE_CLIENT_ID,
                    ONEDRIVE_TENANT_ID,
                    ONEDRIVE_CLIENT_SECRET,
                    ONEDRIVE_PRINCIPLE_NAME)
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import CSVLoader
from llama_index.core import download_loader
from llama_index.readers.microsoft_onedrive import OneDriveReader
from pypdf import PdfReader
from services.query.data_source import DataSource, CHUNK_SIZE, DataSourceFile
from utils.errors import NoDocumentsIndexedException
from utils import text_helper
from utils.gcs_helper import create_bucket, upload_to_gcs

# pylint: disable=broad-exception-caught

# text chunk size for embedding data
Logger = Logger.get_logger(__file__)

class SharePointDataSource(DataSource):
  """
  Class for sharepoint data sources.
  """

  def __init__(self, storage_client):
    self.storage_client = storage_client
    self.docs_not_processed = []

  def download_documents(self, doc_url: str, temp_dir: str) -> \
        List[DataSourceFile]:
    """
    Download files from doc_url source to a local tmp directory

    Args:
        doc_url: folder path on OneDrive
        temp_dir: Path to temporary directory to download files to

    Returns:
        list of DataSourceFile
    """
    downloaded_docs = []
    
    # extract folder name from url
    sharepoint_folder = doc_url.split("shpt://")[1]

    if self.bucket_name is None:
      Logger.error(
      f"ERROR: Bucket name for SharepointDataSource {doc_url} not set. "
      f"Scraped files not uploaded to Google Cloud Storage")
    else:
      # ensure downloads bucket exists, and clear contents
      create_bucket(self.storage_client, self.bucket_name)
    
    # download files to local storage
    loader = OneDriveReader(
        client_id=ONEDRIVE_CLIENT_ID,
        tenant_id=ONEDRIVE_TENANT_ID,
        client_secret=ONEDRIVE_CLIENT_SECRET
    )
    documents = loader.load_data(
        folder_path=sharepoint_folder,
        userprincipalname=ONEDRIVE_PRINCIPLE_NAME
    )
    
    # upload files to GCS and create list of DataSourceFile objects
    for doc in documents:
      file_name = doc.metadata["name"]
      local_path = doc.metadata.keys()[0]
      content_type = doc.metadata["mime_type"]
      with open(local_path, "r", encoding="utf-8") as f:
        file_content = f.read()

      # upload doc to GCS
      gcs_path = upload_to_gcs(self.storage_client, self.bucket_name,
                               file_name, file_content, content_type)
      
      # create DataSourceFile object to track download
      datasource_file = DataSourceFile(
        doc_name = doc.metadata["name"]
        src_url = doc.metadata["name"]
        local_path = doc.metadata.keys()[0]
        gcs_path = gcs_path
      )
      downloaded_docs.append(datasource_file)

    return downloaded_docs
