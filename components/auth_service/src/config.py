# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
  Authentication service config file
"""
# pylint: disable=line-too-long,broad-exception-caught
import os
from google.cloud import secretmanager
from common.utils.logging_handler import Logger
from schemas.error_schema import (UnauthorizedUserErrorResponseModel,
                                  InternalServerErrorResponseModel,
                                  ValidationErrorResponseModel,
                                  ConnectionErrorResponseModel)

secret_client = secretmanager.SecretManagerServiceClient()

PORT = os.environ["PORT"] if os.environ.get("PORT") is not None else 80
PROJECT_ID = os.environ.get("PROJECT_ID", "")
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")
API_BASE_URL = os.getenv("API_BASE_URL")
IDP_URL = "https://identitytoolkit.googleapis.com/v1/accounts"

# If this flag is "true", all sign-in/sign-up requires a pre-existing
# Firestore User record in "users" collection.
AUTH_REQUIRE_FIRESTORE_USER = os.getenv(
    "AUTH_REQUIRE_FIRESTORE_RECORD", "").lower() == "true"

# Retrieving FIREBASE_API_KEY from secrets manager.
FIREBASE_API_KEY = None
try:
  FIREBASE_API_KEY = secret_client.access_secret_version(
      request={
          "name":
              "projects/" + PROJECT_ID +
              "/secrets/firebase-api-key/versions/latest"
      }).payload.data.decode("utf-8")
  FIREBASE_API_KEY = FIREBASE_API_KEY.strip()
except Exception as e:
  Logger.error("Unable to retrieve FIREBASE_API_KEY from "
               "secret [firebase-api-key]")
  raise e

ERROR_RESPONSES = {
    500: {
        "model": InternalServerErrorResponseModel
    },
    503: {
        "model": ConnectionErrorResponseModel
    },
    401: {
        "model": UnauthorizedUserErrorResponseModel
    },
    422: {
        "model": ValidationErrorResponseModel
    }
}

# Make sure all required constants are set.
assert PROJECT_ID
assert FIREBASE_API_KEY
