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

"""Utility methods for token validation."""
from google.auth.transport import requests
from google.oauth2 import id_token
from firebase_admin.auth import verify_id_token

from common.utils.cache_service import set_key, get_key
from common.utils.errors import InvalidTokenError
from common.utils.http_exceptions import InternalServerError, Unauthenticated
from common.utils.logging_handler import Logger


Logger = Logger.get_logger(__file__)


def get_token_cache(token):
  cached_token = None
  try:
    cached_token = get_key(f"cache::{token}")
  except ConnectionError as e:
    Logger.error(f"Unable to get token to Redis cache: {e.message}")

  return cached_token

def set_token_cache(token, decoded_token):
  cached_token = None
  try:
    cached_token = set_key(f"cache::{token}", decoded_token, 1800)
  except ConnectionError as e:
    Logger.error(f"Unable to set token to Redis cache: {e.message}")

  return cached_token


def verify_firebase_token(token):
  """
    Verifies id token issued to user, Return user authentication
    details is token is valid, else Returns token expired as error
    Args:
        ID Token: String
    Returns:
        User auth details: Dict
  """
  return verify_id_token(token)


def validate_token(bearer_token):
  """
    Validates Token passed in headers, Returns user
    auth details along with user_type = new or old
    In case of Invalid token Throws error
    Args:
        Bearer Token: String
    Returns:
        Decoded Token and User type: Dict
  """
  token = bearer_token
  decoded_token = None

  cached_token = get_token_cache(f"cache::{token}")
  decoded_token = cached_token if cached_token else verify_id_token(token)
  if not cached_token:
    cached_token = set_token_cache(f"cache::{token}", decoded_token)
    Logger.info(f"Id Token caching status: {cached_token}")

  Logger.info(f"Id Token: {decoded_token}")
  return decoded_token


def validate_google_oauth_token(token):
  try:
    # If the ID token is valid. Get the user's Google Account ID from the
    # decoded token.
    return id_token.verify_oauth2_token(token, requests.Request())
  except (ValueError, InvalidTokenError) as e:
    raise Unauthenticated(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e
