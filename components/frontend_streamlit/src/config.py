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
from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)

PROJECT_ID = os.environ.get("PROJECT_ID", None)
API_BASE_URL = os.environ.get("API_BASE_URL", None)
APP_BASE_PATH = os.environ.get("APP_BASE_PATH", "/streamlit")

assert API_BASE_URL, "API_BASE_URL is not defined."

LLM_SERVICE_PATH = "llm-service/api/v1"
JOBS_SERVICE_PATH = "jobs-service/api/v1"
AUTH_SERVICE_PATH = "authentication/api/v1"

LLM_SERVICE_API_URL = os.environ.get("LLM_SERVICE_API_URL",
                                     f"{API_BASE_URL}/{LLM_SERVICE_PATH}")
JOBS_SERVICE_API_URL = os.environ.get("JOBS_SERVICE_API_URL",
                                     f"{API_BASE_URL}/{JOBS_SERVICE_PATH}")
AUTH_SERVICE_API_URL = os.environ.get("AUTH_SERVICE_API_URL",
                                     f"{API_BASE_URL}/{AUTH_SERVICE_PATH}")

print(f"APP_BASE_PATH = {APP_BASE_PATH}")
print(f"API_BASE_URL = {API_BASE_URL}")
print(f"LLM_SERVICE_API_URL = {LLM_SERVICE_API_URL}")
print(f"JOBS_SERVICE_API_URL = {JOBS_SERVICE_API_URL}")
print(f"AUTH_SERVICE_API_URL = {AUTH_SERVICE_API_URL}")
