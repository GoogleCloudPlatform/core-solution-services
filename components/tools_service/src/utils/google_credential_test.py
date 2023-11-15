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
utility methods to execute unit tests for module gmail_service.py
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import

import os
import pytest
from unittest import mock
from unittest.mock import Mock
from unittest.mock import patch
from common.testing.firestore_emulator import (firestore_emulator,
                                               clean_firestore)

with mock.patch(
  "google.cloud.logging.Client", side_effect=mock.MagicMock()) as mok:
  from utils.google_credential import get_google_credential


os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"

MOCK_CREDENTIAL = {
  "IdToken": "fake_token",
}

@patch("builtins.open", mock.mock_open())
@mock.patch("utils.google_credential.get_gmail_credentials")
def test_send_email(
    mock_get_gmail_credentials):
  # arrange
  mock_get_gmail_credentials.return_value = MOCK_CREDENTIAL

  # action
  cred = get_google_credential()

  # assert
  assert cred == MOCK_CREDENTIAL
