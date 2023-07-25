"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

""" Helper Functions"""
import json
from google.cloud import secretmanager
import google_crc32c
import ttl_cache
from config import PROJECT_ID


@ttl_cache(3600)
def get_gke_pd_sa_key_from_secret_manager():
  """Get GKE Pod service account keys from
    Secret manager
  Args:
  Returns:
  return the POD service account keys in JSON format
  """ ""

  client = secretmanager.SecretManagerServiceClient()
  secret_id = "gke-pod-sa-key"
  secret_name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"

  response = client.access_secret_version(request={"name": secret_name})
  crc32c = google_crc32c.Checksum()
  crc32c.update(response.payload.data)
  if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
    print("Data corruption detected.")
    return response
  payload = response.payload.data.decode("UTF-8")
  response = json.loads(payload)
  return response


@ttl_cache(3600)
def get_offline_access_token_from_secret_manager():
  """_summary_

  Returns:
      dict: offline access token
  """
  client = secretmanager.SecretManagerServiceClient()
  secret_id = "registration_access_token"
  secret_name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"

  response = client.access_secret_version(request={"name": secret_name})
  crc32c = google_crc32c.Checksum()
  crc32c.update(response.payload.data)
  if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
    print("Data corruption detected.")
    return response
  payload = response.payload.data.decode("UTF-8")
  response = json.loads(payload)
  return response

