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
from typing import List
from common.utils.logging_handler import Logger
from common.models import QueryEngine
from config import (PROJECT_ID,
                    ONEDRIVE_CLIENT_ID,
                    ONEDRIVE_TENANT_ID,
                    ONEDRIVE_CLIENT_SECRET,
                    ONEDRIVE_PRINCIPLE_NAME)
from llama_index.readers.microsoft_onedrive import OneDriveReader
from services.query.data_source import DataSource, DataSourceFile
from utils.gcs_helper import create_bucket, upload_to_gcs

# pylint: disable=broad-exception-caught

# text chunk size for embedding data
Logger = Logger.get_logger(__file__)

class SharePointDataSource(DataSource):
  """
  Class for sharepoint data sources.
  """

  def __init__(self, storage_client, bucket_name=None):
    """
    Initialize the SharePointDataSource.

    Args:
      storage_client: Google cloud storage client instance
      bucket_name (str): name of GCS bucket to save downloaded documents.
                         If None files will not be saved to GCS.
    """
    super().__init__(storage_client)
    self.bucket_name = bucket_name
    self.doc_data = []

  def download_documents(self, doc_url: str, temp_dir: str) -> \
        List[DataSourceFile]:
    """
    Download files from doc_url source to a local tmp directory

    Args:
        doc_url: shpt://<folder path on OneDrive>
        temp_dir: Path to temporary directory to download files to

    Returns:
        list of DataSourceFile
    """
    # extract folder name from url
    sharepoint_folder = doc_url.split("shpt://")[1]

    if self.bucket_name is None:
      Logger.error(
      f"ERROR: Bucket name for SharePointDataSource {doc_url} not set. "
      f"Downloaded files will not be uploaded to Google Cloud Storage")
    else:
      # ensure downloads bucket exists, and clear contents
      create_bucket(self.storage_client, self.bucket_name)
    
    # download files to local storage
    loader = OneDriveReader(
        client_id=ONEDRIVE_CLIENT_ID,
        tenant_id=ONEDRIVE_TENANT_ID,
        client_secret=ONEDRIVE_CLIENT_SECRET,
        userprincipalname=ONEDRIVE_PRINCIPLE_NAME,
        folder_path=sharepoint_folder
    )
    # download files from sharepoint to local dir
    datasource_files = _download_sharepoint_files(loader, temp_dir, sharepoint_folder)
    
    # upload files to GCS
    if self.bucket_name:
      bucket = self.storage_client.get_bucket(self.bucket_name)
      for doc in datasource_files:
        blob = bucket.blob(doc.doc_name)
        blob.upload_from_filename(doc.local_path)
        doc.gcs_path = blob.path

    return datasource_files

  def _download_sharepoint_files(
      loader: OneDriveReader,
      temp_dir: str,
      sharepoint_folder: str) -> List[DataSourceFile]:
    """ Use llamaindex sharepoint loader to download files locally """
    datasource_files = []
    access_token = loader._authenticate_with_msal()
    doc_metadata = loader._connect_download_and_return_metadata(
        access_token, 
        temp_dir, 
        sharepoint_folder, 
        False, 
        userprincipalname=loader.userprincipalname,
        isRelativePath=True
    )
    
    for doc_path, doc_data in doc_metadata.items():    
      # create DataSourceFile object
      datasource_file = DataSourceFile(
        doc_name = doc_data["file_name"],
        src_url = doc_data["file_id"],
        local_path = doc_path
      )
      datasource_files.append(datasource_file)
    return datasource_files
