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
  Unit tests for Authentication endpoint
"""
from fastapi import FastAPI
from fastapi.testclient import TestClient
from schemas.schema_examples import BASIC_VALIDATE_TOKEN_RESPONSE_EXAMPLE
from routes.validate_token import router
from common.utils.http_exceptions import add_exception_handlers
from common.models import User

API_URL = "http://localhost/authentication/api/v1"
FAKE_USER_DATA = {
    "id": "fake-user-id",
    "user_id": "fake-user-id",
    "email": "api-testing@test.com",
    "status": "active",
    "user_type": "user",
    "access_api_docs": False,
}

app = FastAPI()
app.include_router(router, prefix="/authentication/api/v1")
add_exception_handlers(app)

client = TestClient(app)
fake_user = User.from_dict(FAKE_USER_DATA)

def test_valid_id(mocker):
  token = "Bearer cXVhbnRpcGhpX3NuaHU6ODc2MnRhZQ=="
  url = f"{API_URL}/validate"
  mocker.patch(
      "routes.validate_token.validate_token",
      return_value=BASIC_VALIDATE_TOKEN_RESPONSE_EXAMPLE)
  mocker.patch(
      "routes.validate_token.get_user_by_email",
      return_value=fake_user)

  response = client.get(url, headers={"Authorization": token})
  assert response.json().get("data") == BASIC_VALIDATE_TOKEN_RESPONSE_EXAMPLE

def test_valid_id_no_header():
  url = f"{API_URL}/validate"
  response = client.get(url, headers={})
  assert response.json().get("message") == "Token not found"
