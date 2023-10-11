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
    utility methods to execute unit tests for module firebase_authentication.py
"""
import mock
from services.firebase_authentication import verify_token

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


@mock.patch("services.firebase_authentication.auth")
def test_verify_token(mock_auth):
  # arrange
  token = "token"
  mock_auth.verify_id_token.return_value = auth_details

  # action
  decoded_token = verify_token(token)

  # action
  assert decoded_token == auth_details
