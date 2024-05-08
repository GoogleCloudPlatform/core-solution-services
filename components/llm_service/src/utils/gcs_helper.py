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

# pylint: disable=unused-argument,broad-exception-raised
"""
Google Storage helper functions.
"""
from pathlib import Path
from typing import List
from common.utils.logging_handler import Logger
from google.cloud import storage

Logger = Logger.get_logger(__file__)

def clear_bucket(storage_client: storage.Client, bucket_name: str) -> None:
  """
  Delete all the contents of the specified GCS bucket
  """
  Logger.info(f"Deleting all objects from GCS bucket {bucket_name}")
  bucket = storage_client.bucket(bucket_name)
  blobs = bucket.list_blobs()
  index = 0
  for blob in blobs:
    blob.delete()
    index += 1
  Logger.info(f"{index} files deleted")

def create_bucket(storage_client: storage.Client,
                  bucket_name: str, location: str = None,
                  clear: bool = True,
                  make_public: bool = False) -> None:
  # Check if the bucket exists
  bucket = storage_client.bucket(bucket_name)
  if not bucket.exists():
    # Create new bucket
    if make_public:
      _ = storage_client.create_bucket(bucket_name, location=location)
      set_bucket_viewer_iam(storage_client, bucket_name, ["allUsers"])
    else:
      _ = storage_client.create_bucket(bucket_name, location=location)
    Logger.info(f"Bucket {bucket_name} created.")
  else:
    Logger.info(f"Bucket {bucket_name} already exists.")
    if clear:
      clear_bucket(storage_client, bucket_name)

def set_bucket_viewer_iam(
    storage_client: storage.Client,
    bucket_name: str,
    members: List[str] = None,
):
  """Set viewer IAM Policy on bucket"""
  if members is None:
    members = ["allUsers"]
  bucket = storage_client.bucket(bucket_name)
  policy = bucket.get_iam_policy(requested_policy_version=3)
  policy.bindings.append(
      {"role": "roles/storage.objectViewer", "members": members}
  )
  bucket.set_iam_policy(policy)

def upload_to_gcs(storage_client: storage.Client, bucket_name: str,
                  file_path: str) -> str:
  """ Upload file to GCS bucket. Returns URL to file. """
  Logger.info(f"Uploading {file_path} to GCS bucket {bucket_name}")
  bucket = storage_client.bucket(bucket_name)
  file_name = Path(file_path).name
  blob = bucket.blob(file_name)
  blob.upload_from_filename(file_path)
  gcs_url = f"gs://{bucket_name}/{file_name}"
  Logger.info(f"Uploaded {file_path} to {gcs_url}")
  return gcs_url
