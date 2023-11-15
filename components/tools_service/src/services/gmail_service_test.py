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
from common.testing.firestore_emulator import (firestore_emulator,
                                               clean_firestore)

with mock.patch(
  "google.cloud.logging.Client", side_effect=mock.MagicMock()) as mok:
  from services.gmail_service import send_email


os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"

MOCK_EMAIL_CONTENT = {
  "recipient": "test@example.com",
  "subject": "Hello",
  "message": "From the world."
}

@mock.patch("services.gmail_service.get_google_credential")
@mock.patch("services.gmail_service.build_resource_service")
@mock.patch("services.gmail_service.GmailToolkit")
def test_send_email(
    mock_gmail_toolkit,
    mock_build_resource_service,
    mock_get_google_credential):
  # arrange
  mock_tool = Mock()
  mock_tool.invoke.return_value = "Message sent."
  mock_toolkit = Mock()
  mock_toolkit.get_tools.return_value = [{}, mock_tool]
  mock_gmail_toolkit.return_value = mock_toolkit
  mock_build_resource_service.return_value = {}
  mock_get_google_credential.return_value = {}

  # action
  result = send_email(
    MOCK_EMAIL_CONTENT["recipient"],
    MOCK_EMAIL_CONTENT["subject"],
    MOCK_EMAIL_CONTENT["message"])

  # assert
  assert result is not None
  assert result == "Message sent."
