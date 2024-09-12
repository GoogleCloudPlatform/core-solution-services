# Copyright 2023 Google LLC
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
File processing helper functions.
"""
# pylint: disable=broad-exception-caught

import os
import tempfile
from typing import Union
from urllib.parse import urlparse
from base64 import b64decode
from fastapi import UploadFile
from config import PAYLOAD_FILE_SIZE, PROJECT_ID
from common.utils.errors import (PayloadTooLargeError,
                                 ValidationError, UnsupportedError)
from common.utils.logging_handler import Logger
from utils.gcs_helper import create_bucket_for_file, upload_file_to_gcs
from google.cloud import storage
from services.query.web_datasource import WebDataSource

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
        if chat_file_type is None:
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

async def process_upload_file(upload_file: UploadFile, bucket=None) -> str:
  """
  Read the content for an upload file.
  Also upload the file to a GCS bucket.

  Args:
      upload_file: FastAPI upload file
      bucket (optional): existing bucket for file upload

  Returns:
      URL of uploaded file
  """
  # check upload file size
  if upload_file.size > PAYLOAD_FILE_SIZE:
    raise PayloadTooLargeError(
      f"File size is too large: {upload_file.filename}"
    )

  # create bucket for file
  if bucket is None:
    bucket = create_bucket_for_file(upload_file.filename)

  # upload file to bucket
  await upload_file.seek(0)
  upload_file_url = \
      upload_file_to_gcs(bucket, upload_file.filename, upload_file.file)

  # rewind file after upload
  await upload_file.seek(0)

  return upload_file_url

def validate_multi_file_type(file_name, file_b64=None) -> Union[str, None]:
  """
  Determine the mime type based on file extension.  Validate that the file
  is supported as a multimodal file type for Vertex.

  For byte files, validate the file header to ensure that it is
  a type supported by Vertex multimodal LLMs.

  Args:
      file_name: name of file
      file_b64 (optional): b64 encoded file content

  Returns:
      mime type of file or None if unsupported mime type or mime type
        cannot be determined
  """
  vertex_mime_types = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".mov": "video/mov",
    ".avi": "video/avi",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpg",
    ".wmv": "video/wmv",
    ".html": "text/html",
    ".htm": "text/html",
    ".pdf": "application/pdf"
  }
  file_extension = os.path.splitext(file_name)[1]
  mime_type = vertex_mime_types.get(file_extension)
  if not mime_type:
    return None

  # Make sure that the user file b64 is a valid image or video
  if file_b64:
    image_signatures = {
        b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
        b"\xFF\xD8\xFF": "jpg",
        b"\xFF\xD8": "jpeg",
        b"\x47\x49\x46\x38": "gif",
        b"\x00\x00\x00 ftyp": "mp4",
        b"\x00\x00\x00\x14": "mov",
        b"RIFF": "avi",
        b"\x00\x00\x01\xba!\x00\x01\x00": "mpeg",
        b"\x00\x00\x01\xB3": "mpg",
        b"0&\xb2u\x8ef\xcf\x11": "wmv"
    }
    file_header = b64decode(file_b64)[:8]  # Get the first 8 bytes
    user_file_type = None
    for sig, file_format in image_signatures.items():
      if file_header.startswith(sig):
        user_file_type = file_format
        break
    if not user_file_type:
      return None

  return mime_type
