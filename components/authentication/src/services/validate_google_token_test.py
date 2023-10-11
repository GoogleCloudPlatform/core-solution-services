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
utility methods to execute unit tests for module validate_google_token.py
"""
from unittest import mock
from services.validate_google_token import validate_google_oauth_token
from schemas.schema_examples import DECODED_TOKEN_EXAMPLE

token = "eyewiuovnhy3b.oiuewvryn919123b85n913vnp19qvm92vb.w9euvyn0f091823b"


@mock.patch("services.validate_google_token.id_token.verify_oauth2_token")
def test_validate_google_token(mock_validate_google_oauth_token):

  mock_validate_google_oauth_token.return_value = DECODED_TOKEN_EXAMPLE
  result = validate_google_oauth_token(token)

  assert result["email"] == DECODED_TOKEN_EXAMPLE["email"]
