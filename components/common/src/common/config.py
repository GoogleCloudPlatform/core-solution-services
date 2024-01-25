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
Config module to setup common environment
"""
import os

PROJECT_ID = os.environ.get("PROJECT_ID",
                            os.environ.get("GOOGLE_CLOUD_PROJECT"))

API_BASE_URL = os.getenv("API_BASE_URL")
BQ_REGION = os.getenv("BQ_REGION", "US")
CLASSROOM_ADMIN_EMAIL = os.getenv("CLASSROOM_ADMIN_EMAIL")
CLOUD_LOGGING_ENABLED = bool(
    os.getenv("CLOUD_LOGGING_ENABLED", "true").lower() in ("true",))
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
GKE_SERVICE_ACCOUNT_NAME = os.getenv("GKE_SERVICE_ACCOUNT_NAME", "gke-sa")
PUB_SUB_PROJECT_ID = os.getenv("PUB_SUB_PROJECT_ID", PROJECT_ID)
SERVICE_NAME = os.getenv("SERVICE_NAME")
REGION = os.getenv("REGION", "us-central1")

# TODO: Automate this with existing GKE service names.
SERVICES = {
    "authentication": {
        "host": "authentication",
        "port": 80
    },
    "user-management": {
        "host": "user-management",
        "port": 80
    },
    "llm-service": {
        "host": "llm-service",
        "port": 80
    },
    "rules-engine": {
        "host": "rules-engine",
        "port": 80
    },
    "tools-service": {
        "host": "tools-service",
        "port": 80
    },
}

CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "").split(",")
