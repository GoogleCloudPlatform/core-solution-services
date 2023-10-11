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

"""Utility method for Token generation."""
import requests
from config import FIREBASE_API_KEY
from utils.exception_handler import InvalidRefreshTokenError


def generate_token(req_body):
  """
    Calls get_id_token method from refresh_token_service
    and Returns Response or Error.
    Args:
        req_body: Dict
    Returns
        token_credentials: Dict
  """

  payload = (
      f"grant_type=refresh_token&"
      f"refresh_token={req_body['refresh_token']}"
  )
  response = get_id_token(payload)
  if "error" in response:
    raise InvalidRefreshTokenError(response["error"]["message"])
  return response


def get_id_token(payload):
  """
    Calls Google API using refresh_token as payload to generate
    new Id Token
    Args:
        payload: Dict(Object)
        API_KEY: String
    Returns:
        Token Credentials: Dict(Object)
  """
  resp = requests.post(
      "https://securetoken.googleapis.com/v1/token",
      payload,
      headers={"Content-Type": "application/x-www-form-urlencoded"},
      params={"key": FIREBASE_API_KEY},
      timeout=60)
  return resp.json()
