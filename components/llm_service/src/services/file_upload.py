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


""" Services for multi modal file uploads """
import os
import tempfile
from urllib.parse import urlparse
from common.utils.logging_handler import Logger
from common.utils.errors import ValidationError, UnsupportedError
from config import PROJECT_ID
from google.cloud import storage
from services.query.web_datasource import WebDataSource
from utils.file_helper import process_upload_file, validate_multi_file_type
from utils.gcs_helper import create_bucket_for_file

Logger = Logger.get_logger(__file__)

async def process_chat_file(chat_file,
                            chat_file_url,
                            depth_limit=0):
  """
  Process a chat upload file.
  
  Upload the file to GCS, or in the case of a web URL, download the HTML files
  to GCS.

  Also determine the mime type of the content.
  
  Returns:
    list of URLs of chat files, Mime type of file
  """
  chat_file_type = None
  chat_file_urls = None
  is_valid = False
  if chat_file is not None:
    bucket = create_bucket_for_file(chat_file.filename)
    if chat_file_url is not None:
      raise ValidationError("cannot set both upload_file and file_url")
    chat_file_url = await process_upload_file(chat_file, bucket)
    chat_file_type = validate_multi_file_type(chat_file.filename)
    if chat_file_type is None:
      raise ValidationError(
          f"unsupported file type upload file {chat_file.filename}")
  elif chat_file_url:
    parsed_url = urlparse(chat_file_url)

    # validate url is supported protocol
    if not parsed_url.scheme in ["gs", "http", "https", "shpt"]:
      raise ValidationError(
          "chat_file_url must start with gs://, http:// or https://, shpt://")

    # validate file type from extension if present
    chat_file_name = parsed_url.path
    if chat_file_name:
      file_extension = os.path.splitext(chat_file_name)[1]
      if file_extension:
        chat_file_type = validate_multi_file_type(chat_file_name)
        if not is_valid:
          raise ValidationError(
              f"unsupported file type file url {chat_file_url}")
    else:
      # assume html if no extension
      chat_file_type = "text/html"

    storage_client = storage.Client(project=PROJECT_ID)
    if parsed_url.scheme in ["http", "https"]:
      # download web site files
      chat_file_path = chat_file_url.split("://")[1]
      bucket = create_bucket_for_file(chat_file_path)
      web_data_source = WebDataSource(storage_client,
                                      bucket_name=bucket.name,
                                      depth_limit=depth_limit)
      with tempfile.TemporaryDirectory() as temp_dir:
        data_source_files = \
            web_data_source.download_documents(chat_file_url, temp_dir)
        chat_file_urls = [f.gcs_url for f in data_source_files]
    elif chat_file_url.startswith("shpt://"):
      raise UnsupportedError("shpt:// not supported for chat upload")
    elif chat_file_url.startswith("gs://"):
      # process gcs url
      bucket = storage_client.bucket(parsed_url.netloc)
      if not parsed_url.path:
        blobs = storage_client.list_blobs(
            bucket.name,
            delimiter="/",
            include_trailing_delimiter=True)
        chat_file_urls = [f"gs://{blob.name}" for blob in blobs]
      else:
        chat_file_urls = [chat_file_url]

  Logger.info(f"process_chat_upload: {chat_file_urls} type {chat_file_type}")

  return chat_file_urls, chat_file_type

