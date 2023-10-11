# Copyright 2023 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
  Authentication service config file
"""
import os
from schemas.error_schema import (UnauthorizedUserErrorResponseModel,
                                  InternalServerErrorResponseModel,
                                  ValidationErrorResponseModel)

PORT = os.environ["PORT"] if os.environ.get("PORT") is not None else 80

PROJECT_ID = os.environ.get("PROJECT_ID", "")
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID

DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")

API_BASE_URL = os.getenv("API_BASE_URL")

SERVICE_NAME = os.getenv("SERVICE_NAME")

REDIS_HOST = os.getenv("REDIS_HOST")

FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

IDP_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

IS_DEVELOPMENT = bool(os.getenv("IS_DEVELOPMENT", "").lower() in ("True",
                                                                  "true"))

AUTHENTICATION_VERSION = os.getenv("AUTHENTICATION_VERSION", "v1")

ERROR_RESPONSES = {
  500: {
    "model": InternalServerErrorResponseModel
  },
  401: {
    "model": UnauthorizedUserErrorResponseModel
  },
  422: {
    "model": ValidationErrorResponseModel
  }
}
