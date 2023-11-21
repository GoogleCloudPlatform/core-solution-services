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
  Streamlit app config file
"""
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught

import os
from google.cloud import secretmanager
from common.utils.logging_handler import Logger
from common.utils.token_handler import UserCredentials

Logger = Logger.get_logger(__file__)
secrets = secretmanager.SecretManagerServiceClient()

PROJECT_ID = os.environ.get("PROJECT_ID", None)
API_BASE_URL = os.environ.get("API_BASE_URL", None)
APP_BASE_PATH = "/streamlit"

try:
  LLM_BACKEND_ROBOT_USERNAME = secrets.access_secret_version(
      request={
          "name":
              f"projects/{PROJECT_ID}" +
              "/secrets/llm-backend-robot-username/versions/latest"
      }).payload.data.decode("utf-8")
  LLM_BACKEND_ROBOT_USERNAME = LLM_BACKEND_ROBOT_USERNAME.strip()
except Exception as e:
  LLM_BACKEND_ROBOT_USERNAME = None

try:
  LLM_BACKEND_ROBOT_PASSWORD = secrets.access_secret_version(
      request={
          "name":
              f"projects/{PROJECT_ID}" +
              "/secrets/llm-backend-robot-password/versions/latest"
      }).payload.data.decode("utf-8")
  LLM_BACKEND_ROBOT_PASSWORD = LLM_BACKEND_ROBOT_PASSWORD.strip()
except Exception as e:
  LLM_BACKEND_ROBOT_PASSWORD = None

# Update this config for local development or notebook usage, by adding
# a param to the UserCredentials class initializer, to pass URL to auth client
# auth_client = UserCredentials(LLM_BACKEND_ROBOT_USERNAME,
#                               LLM_BACKEND_ROBOT_PASSWORD,
#                               "http://localhost:9004")
# pass URL to auth client for external routes to auth.  Replace dev.domain with
# the externally mapped domain for your dev server
# auth_client = UserCredentials(LLM_BACKEND_ROBOT_USERNAME,
#                               LLM_BACKEND_ROBOT_PASSWORD,
#                               "https://[dev.domain]")

auth_client = UserCredentials(LLM_BACKEND_ROBOT_USERNAME,
                              LLM_BACKEND_ROBOT_PASSWORD)
