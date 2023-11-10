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

"""Utility methods for token validation."""
from google.auth.transport import requests
from google.oauth2 import id_token
import firebase_admin
from firebase_admin import auth

from common.models import TempUser
from common.utils.cache_service import set_key, get_key
from common.utils.errors import UnauthorizedUserError, InvalidTokenError
from common.utils.http_exceptions import InternalServerError, Unauthenticated
from common.utils.logging_handler import Logger


default_app = firebase_admin.initialize_app()

def validate_token(bearer_token):
  """
    Validates Token passed in headers, Returns user
    auth details along with user_type = new or old
    In case of Invalid token Throws error
    Args:
        Bearer Token: String
    Returns:
        Decoded Token and User type: Dict
  """
  token = bearer_token
  decoded_token = auth.verify_id_token(token)
  token_data = {**decoded_token}
  Logger.info(f"Id Token: {token_data}")

  user = TempUser.find_by_email(decoded_token["email"])
  if user is not None:
    user_fields = user.get_fields(reformat_datetime=True)
    if user_fields.get("status") == "inactive":
      raise UnauthorizedUserError("Unauthorized")
    token_data["access_api_docs"] = False if user_fields.get(
        "access_api_docs") is None else user_fields.get("access_api_docs")
    token_data["user_type"] = user_fields.get("user_type")
  else:
    raise UnauthorizedUserError("Unauthorized")
  return token_data


def validate_google_oauth_token(token):
  try:
    # If the ID token is valid. Get the user's Google Account ID from the
    # decoded token.
    return id_token.verify_oauth2_token(token, requests.Request())
  except (ValueError, InvalidTokenError) as e:
    raise Unauthenticated(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e
