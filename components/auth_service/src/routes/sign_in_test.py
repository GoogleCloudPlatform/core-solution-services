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
  Unit tests for Sign In endpoints
"""
# pylint: disable=unused-argument,unused-import
from unittest import mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routes.sign_in import router
from testing.test_config import API_URL
from common.testing.firestore_emulator import (firestore_emulator,
                                               clean_firestore)
from common.utils.http_exceptions import add_exception_handlers
from schemas.schema_examples import (
  SIGN_IN_WITH_CREDENTIALS_API_INPUT_EXAMPLE,
  SIGN_IN_WITH_CREDENTIALS_API_RESPONSE_EXAMPLE,
  SIGN_IN_WITH_TOKEN_RESPONSE_EXAMPLE,
  SIGN_IN_WITH_TOKEN_RESPONSE_NEGATIVE_EXAMPLE,
  SIGN_IN_WITH_CREDENTIALS_RESPONSE_NEGATIVE_EXAMPLE, DECODED_TOKEN_EXAMPLE)

app = FastAPI()
app.include_router(router, prefix="/auth-service/api/v1")
add_exception_handlers(app)

client_with_emulator = TestClient(app)

# assigning url
api_url = f"{API_URL}/sign-in"


@mock.patch("routes.sign_in.requests.post")
@mock.patch("routes.sign_in.create_session")
@mock.patch("routes.sign_in.validate_google_oauth_token")
def test_sign_in_with_token(mock_token_res, mock_session, mock_request):
  url = f"{api_url}/token"

  token = "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImU4NDdkOTk0OGU4NTQ1OTQ4ZmE4MTU3Y"
  headers = {"Authorization": token}
  mock_token_res.return_value = {
    **DECODED_TOKEN_EXAMPLE,
    "user_id": "asd98798as7dhjgkjsdfh"
  }
  mock_session.return_value = {"session_id": "asd98798as7dhjgkjsdfh"}
  mock_request.return_value.status_code = 200
  mock_request.return_value.json.return_value = (
    SIGN_IN_WITH_TOKEN_RESPONSE_EXAMPLE)

  resp = client_with_emulator.post(url, headers=headers)
  assert resp.status_code == 200, "Status should be 200"
  assert resp.json().get("data") == mock_request.return_value.json.return_value


@mock.patch("routes.sign_in.requests.post")
@mock.patch("routes.sign_in.validate_google_oauth_token")
def test_sign_in_with_token_negative(mock_token_res, mock_request):
  url = f"{api_url}/token"

  token = "Bearer eyJhbGcXVhbnRpcGhpX3NuaHU6ODc2MnRhZQ=="
  mock_token_res.return_value = DECODED_TOKEN_EXAMPLE

  mock_request.return_value.status_code = 400
  mock_request.return_value.json.return_value = (
    SIGN_IN_WITH_TOKEN_RESPONSE_NEGATIVE_EXAMPLE)

  resp = client_with_emulator.post(url, headers={"Authorization": token})

  assert resp.status_code == 401, "Status should be 200"
  assert resp.json().get(
    "message") == mock_request.return_value.json.return_value.get(
    "error").get("message")


@mock.patch("routes.sign_in.requests.post")
@mock.patch("routes.sign_in.create_session")
def test_sign_in_with_credentials(mock_session, mock_request):
  url = f"{api_url}/credentials"
  credentials = SIGN_IN_WITH_CREDENTIALS_API_INPUT_EXAMPLE
  mock_session.return_value = {"session_id": "asd98798as7dhjgkjsdfh"}
  mock_request.return_value.status_code = 200
  mock_request.return_value.json.return_value = (
    SIGN_IN_WITH_CREDENTIALS_API_RESPONSE_EXAMPLE)

  resp = client_with_emulator.post(url, json=credentials)
  assert resp.status_code == (
    mock_request.return_value.status_code), "Status should be 200"
  assert resp.json().get("data") == (mock_request.return_value.json.return_value
                                     ), "Incorrect response received"


@mock.patch("routes.sign_in.requests.post")
def test_sign_in_with_credentials_negative(mock_request):
  url = f"{api_url}/credentials"

  credentials = SIGN_IN_WITH_CREDENTIALS_API_INPUT_EXAMPLE

  mock_request.return_value.status_code = 400
  mock_request.return_value.json.return_value = (
    SIGN_IN_WITH_CREDENTIALS_RESPONSE_NEGATIVE_EXAMPLE)

  resp = client_with_emulator.post(url, json=credentials)
  assert resp.status_code == 401, "Status should be 401"
  assert resp.json().get(
    "message") == mock_request.return_value.json.return_value.get(
    "error").get("message"), "Incorrect response received"
