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
Rest Methods
"""
import requests


def post_method(url: str,
                request_body=None,
                query_params=None,
                data=None,
                files=None,
                token=None) -> dict:
  """
    Function for API test POST method
    Parameters
    ----------
    url: str
    request_body: dict
    query_params: dict
    data: dict
    files: File
    token: token
    Returns
    -------
    Json Object
    """

  return requests.post(
      url=f"{url}",
      json=request_body,
      params=query_params,
      data=data,
      files=files,
      headers={"Authorization": token},
      timeout=10
  ).json()


def get_method(url: str, query_params=None, token=None) -> dict:
  """
    Function for API test GET method
    Parameters
    ----------
    url: str
    query_params: dict
    token: token
    Returns
    -------
    JSON Object
    """

  return requests.get(
      url=f"{url}",
      params=query_params,
      headers={"Authorization": token},
      allow_redirects=False,
      timeout=10
  ).json()


def put_method(url: str,
               request_body: dict,
               query_params=None,
               token=None) -> dict:
  """
    Function for API test PUT method
    Parameters
    ----------
    url: str
    request_body: dict
    query_params: dict
    token: token
    Returns
    -------
    JSON Object
    """

  return requests.put(
      url=f"{url}",
      json=request_body,
      params=query_params,
      headers={"Authorization": token},
      timeout=10
  ).json()


def delete_method(url: str, query_params=None, token=None) -> dict:
  """
    Function for API test DELETE method
    Parameters
    ----------
    url: str
    query_params: dict
    token: token
    Returns
    -------
    JSON Object
    """

  return requests.delete(
      url=f"{url}",
      params=query_params,
      headers={"Authorization": token},
      timeout=10
  ).json()
