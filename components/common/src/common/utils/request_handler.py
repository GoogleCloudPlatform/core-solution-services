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
Utilities for calling other platform microservices
"""
import json
import requests
from common.utils.context_vars import get_trace_headers

DEFAULT_TIMEOUT = 300

def get_method(url: str,
               query_params=None,
               auth_client=None,
               token=None,
               timeout=DEFAULT_TIMEOUT) -> json:
  """
  Function for API GET method
  Parameters
  ----------
  url: str
  query_params: dict
  use_bot_account: bool
  token: token
  Returns
  -------
  JSON Object
  """

  if auth_client is not None:
    token = auth_client.get_id_token()

  headers = get_trace_headers()

  if token:
    headers["Authorization"] = f"Bearer {token}"

  return requests.get(
      url=f"{url}", params=query_params,
      headers=headers, timeout=timeout)


def post_method(url: str,
                request_body=None,
                auth_client=None,
                token=None,
                timeout=DEFAULT_TIMEOUT) -> json:
  """
  Function for API POST method
  Parameters
  ----------
  url: str
  request_body: dict
  use_bot_account: bool
  token: token
  Returns
  -------
  JSON Object
  """

  if auth_client is not None:
    token = auth_client.get_id_token()

  headers = get_trace_headers()

  if token:
    headers["Authorization"] = f"Bearer {token}"

  return requests.post(
      url=f"{url}", json=request_body, headers=headers,
      timeout=timeout)


def put_method(url: str,
               request_body=None,
               auth_client=None,
               token=None,
               timeout=DEFAULT_TIMEOUT) -> json:
  """
  Function for API PUT method
  Parameters
  ----------
  url: str
  request_body: dict
  use_bot_account: bool
  token: token
  Returns
  -------
  JSON Object
  """

  if auth_client is not None:
    token = auth_client.get_id_token()

  # Get trace headers
  headers = get_trace_headers()

  if token:
    headers["Authorization"] = f"Bearer {token}"

  return requests.put(
      url=f"{url}", json=request_body, headers=headers,
      timeout=timeout)


def delete_method(url: str,
                  request_body=None,
                  auth_client=None,
                  token=None,
                  timeout=DEFAULT_TIMEOUT) -> json:
  """
  Function for API DELETE method
  Parameters
  ----------
  url: str
  request_body: dict
  use_bot_account: bool
  token: token
  Returns
  -------
  JSON Object
  """

  if auth_client is not None:
    token = auth_client.get_id_token()

  # Get trace headers
  headers = get_trace_headers()

  if token:
    headers["Authorization"] = f"Bearer {token}"

  return requests.delete(
      url=f"{url}", json=request_body, headers=headers,
      timeout=timeout)
