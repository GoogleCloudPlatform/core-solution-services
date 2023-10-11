# Copyright 2023 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Method to validate google auth token"""
from google.oauth2 import id_token
from google.auth.transport import requests
from common.utils.errors import InvalidTokenError
from common.utils.http_exceptions import InternalServerError, Unauthenticated


def validate_google_oauth_token(token):
  try:
    # If the ID token is valid. Get the user's Google Account ID from the
    # decoded token.
    return id_token.verify_oauth2_token(token, requests.Request())
  except (ValueError, InvalidTokenError) as e:
    raise Unauthenticated(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e
