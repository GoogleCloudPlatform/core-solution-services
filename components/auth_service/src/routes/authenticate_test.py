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
  Unit tests for auth-service endpoint
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock

from schemas.schema_examples import BASIC_VALIDATE_TOKEN_RESPONSE_EXAMPLE
from routes.authenticate import router
from common.utils.http_exceptions import add_exception_handlers

API_URL = "http://localhost/auth-service/api/v1"

app = FastAPI()
app.include_router(router, prefix="/auth-service/api/v1")
add_exception_handlers(app)

client = TestClient(app)

@mock.patch("routes.authenticate.validate_token")
def test_valid_id(mock_validate_token):
  token = "Bearer cXVhbnRpcGhpX3NuaHU6ODc2MnRhZQ=="
  url = f"{API_URL}/authenticate"
  mock_validate_token.return_value = BASIC_VALIDATE_TOKEN_RESPONSE_EXAMPLE
  response = client.get(url, headers={"Authorization": token})
  resp_json = response.json()
  assert resp_json.get("data") == BASIC_VALIDATE_TOKEN_RESPONSE_EXAMPLE


def test_valid_id_no_header():
  url = f"{API_URL}/authenticate"
  response = client.get(url, headers={})
  resp_json = response.json()
  assert resp_json.get("message") == "Token not found"
