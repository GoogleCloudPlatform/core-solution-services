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
utility methods to execute unit tests for module validate_token_service.py
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import

import os
import pytest
from unittest import mock

from common.models import TempUser
from common.utils.errors import UnauthorizedUserError
from common.testing.firestore_emulator import (firestore_emulator,
                                               clean_firestore)

with mock.patch(
  "google.cloud.logging.Client", side_effect=mock.MagicMock()) as mok:
  from services.validate_token_service import validate_token
from schemas.schema_examples import BASIC_USER_MODEL_EXAMPLE

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"

auth_details = {
  "name":
    "Test User",
  "picture":
    "https://lh3.googleusercontent.com/-I8CTmvNmtLE\
      /AAAAAAAAAAI/AAAAAAAAAAA/ACHi3rdBqybASKV35NeQTu_cEL5eTO5G9w/photo.jpg",
  "iss":
    "https://securetoken.google.com/my-dummy-project",
  "aud":
    "my-dummy-project",
  "auth_time":
    1579875095,
  "user_id":
    "fiurc756IqcdRSs19upxiVLt1Gr2",
  "sub":
    "fiurc756IqcdRSs19upxiVLt1Gr2",
  "iat":
    1579875097,
  "exp":
    1579878697,
  "email":
    "test.user@gmail.com",
  "email_verified":
    True,
  "firebase": {
    "identities": {
      "google.com": [104415576250754890000],
      "microsoft.com": ["96d7dbe4-0abf-495c-bd1d-cab8af465ac4"],
      "email": ["test.user@gmail.com"]
    },
    "sign_in_provider": "google.com"
  },
  "uid":
    "fiurc756IqcdRSs19upxiVLt1Gr2"
}


@mock.patch("services.validate_token_service.set_key")
@mock.patch("services.validate_token_service.verify_token")
@mock.patch("services.validate_token_service.get_key")
def test_validate_token(mock_get_key, mock_verify_token, mock_set_key,
                        clean_firestore):
  user_dict = {**BASIC_USER_MODEL_EXAMPLE}
  user = TempUser.from_dict(user_dict)
  user.user_id = ""
  user.save()
  user.user_id = user.id
  user.update()
  # arrange
  bearer_token = "Bearer XYZ"
  mock_get_key.return_value = None
  mock_verify_token.return_value = auth_details
  mock_set_key.return_value = True

  # action
  result = validate_token(bearer_token)

  # assert
  assert result is not None
  assert result["name"] == auth_details["name"]
  assert result["email"] == auth_details["email"]
  assert result["user_id"] == auth_details["user_id"]


@mock.patch("services.validate_token_service.get_key")
def test_validate_token_cached(mock_get_key, clean_firestore):
  user_dict = {**BASIC_USER_MODEL_EXAMPLE}
  user = TempUser.from_dict(user_dict)
  user.user_id = ""
  user.save()
  user.user_id = user.id
  user.update()
  # arrange
  bearer_token = "Bearer PQR"
  mock_get_key.return_value = auth_details

  # action
  result = validate_token(bearer_token)

  # assert
  assert result is not None
  assert result["name"] == auth_details["name"]
  assert result["email"] == auth_details["email"]
  assert result["user_id"] == auth_details["user_id"]


@mock.patch("services.validate_token_service.get_key")
def test_validate_token_unauthorized(mock_get_key, clean_firestore):
  # arrange
  bearer_token = "Bearer PQR"
  mock_get_key.return_value = auth_details

  # action
  with pytest.raises(UnauthorizedUserError):
    validate_token(bearer_token)
