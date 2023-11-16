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

""" Secrets Helper Functions"""
import google_crc32c
import requests
import os
from google.cloud import secretmanager

from common.config import PROJECT_ID
from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)
sm_client = secretmanager.SecretManagerServiceClient()


def get_secret(secret_id):
  """Get a generic secret payload from Google Secret Manager

  Args:
      secret_id (str): the id of the secret

  Returns:
      str: the "UTF-8" decoded secret payload
  """
  secret_name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"

  response = sm_client.access_secret_version(request={"name": secret_name})
  crc32c = google_crc32c.Checksum()
  crc32c.update(response.payload.data)
  if response.payload.data_crc32c != int(crc32c.hexdigest(), 16):
    print("Data corruption detected.")
    return response
  payload = response.payload.data.decode("UTF-8")
  payload = payload.strip()
  return payload


# TODO: this should be built into a class that can use refresh token to get
# new id_token, cache token, etc
def get_backend_robot_id_token():
  """Generate an ID Token to be used by the backend robot account for
     service to service authed API calls

  Returns:
      str: the new id_token
  """
  api_endpoint = \
  "http://authentication/authentication/api/v1/sign-in/credentials"
  res = requests.post(url=api_endpoint,
                      headers={
                          "Content-Type": "application/json",
                      },
                      json={
                          "email": get_secret("lms-backend-robot-username"),
                          "password": get_secret("lms-backend-robot-password"),
                      },
                      timeout=60)
  payload = res.json()["data"]
  return payload["idToken"]


def get_env_or_secret(secret_id):
  value = os.getenv(secret_id)
  if value is None:
    try:
      value = get_secret(secret_id)

    except Exception as e:
      # Suppressing all exceptions.
      Logger.error(f"Unable to get secret {secret_id}: {e}")
      value = None

  return value
