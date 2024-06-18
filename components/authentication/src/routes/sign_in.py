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
""" Sign In endpoints """
import requests
import base64
import json
from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from requests.exceptions import ConnectTimeout
from firebase_admin.auth import verify_id_token, get_user, set_custom_user_claims
from common.utils.user_handler import get_user_by_email, create_user_in_firestore
from common.utils.logging_handler import Logger
from common.utils.sessions import create_session
from common.utils.errors import (InvalidTokenError,
                                 UnauthorizedUserError,
                                 InvalidCredentialsError)
from common.utils.http_exceptions import (InternalServerError,
                                          Unauthenticated,
                                          ConnectionTimeout,
                                          ServiceUnavailable)
from schemas.sign_in_schema import (SignInWithCredentialsModel,
                                    SignInWithCredentialsResponseModel,
                                    SignInWithTokenResponseModel)
from services.validation_service import validate_google_oauth_token
from config import (AUTH_REQUIRE_FIRESTORE_USER,
                    FIREBASE_API_KEY,
                    IDP_URL,
                    ERROR_RESPONSES)

# pylint: disable = broad-exception-raised

IDP_SIGN_IN_URL = f"{IDP_URL}:signInWithIdp?key={FIREBASE_API_KEY}"
Logger = Logger.get_logger(__file__)

auth_scheme = HTTPBearer(auto_error=False)

router = APIRouter(
    tags=["Sign In"], prefix="/sign-in", responses=ERROR_RESPONSES)


@router.post("/roles")
def extract_roles_from_auth_provider_token(
  provider_id_token: str, token: auth_scheme = Depends()):
  """This endpoint will take the Firebase id token as an Authorization header
  and the oAuth provider id token and transfer role claims from the auth
  provider to the Firebase user.
  """
  try:
    # validate the Firebase token - throws an error if not valid
    token_dict = dict(token)
    result = verify_id_token(token_dict["credentials"])

    # decode the auth provider id token to retrieve the roles
    payload = provider_id_token.split(".")[1]
    decoded_payload = base64.b64decode(payload)
    decoded_token = json.loads(decoded_payload.decode())

    # check for roles defined by the auth provider
    if "roles" in decoded_token:
      roles = decoded_token["roles"]
      print("Auth provider-defined roles", roles)
    else:
      roles = ["L1"]

    # get the Firebase user
    user_id = result["user_id"]
    user = get_user(user_id)
    if user.custom_claims:
      print("Current Firebase custom claims", user.custom_claims)

    # update firebase user with roles defined by auth provider
    set_custom_user_claims(user_id, { "roles": roles })

    # # check that fierbase auth user has the new roles
    # user = get_user(user_id)
    # print("Updated firebase custom claims", user.custom_claims)

    return {
      "success": True,
      "message":
        f"Successfully retreieved roles from auth provider for {user_id}"
    }

  except (InvalidTokenError, UnauthorizedUserError) as e:
    raise Unauthenticated(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.post("/token", response_model=SignInWithTokenResponseModel)
def sign_in_with_token(token: auth_scheme = Depends()):
  """This endpoint will take the Google oauth token as an Authorization header
  and returns the firebase id_token and refresh token.

  If the user does not exist in the user store a user model will be created.
  """

  try:
    token_dict = dict(token)
    oauth_token = token_dict["credentials"]
    decoded_token = validate_google_oauth_token(oauth_token)
    email = decoded_token.get("email")

    Logger.info(f"request for sign-in: {email}")
    Logger.info(f"decoded_token: {decoded_token}")

    user = get_user_by_email(
        email, check_firestore_user=AUTH_REQUIRE_FIRESTORE_USER)
    data = {
        "requestUri": "http://localhost",
        "returnSecureToken": True,
        "postBody": f"id_token={oauth_token}&providerId=google.com"
    }
    url = f"{IDP_URL}:signInWithIdp?key={FIREBASE_API_KEY}"
    resp = requests.post(url, data, timeout=60)
    resp_json = resp.json()
    Logger.info(f"Response from IDP for sign-in: {resp_json}")

    # Check with non-200 status code
    if resp.status_code == 400:
      raise InvalidTokenError(resp_json.get("error").get("message"))
    if resp.status_code != 200:
      raise Exception(
          f"Error: {resp.status_code} when signing user in ({email}): " +
          resp_json.get("error").get("message"))

    if not user:
      user = create_user_in_firestore({
        "user_id": email,
        "email": email,
      })
    resp_json["user_id"] = user.user_id
    session = create_session(resp_json["user_id"])
    resp_json["session_id"] = session.get("session_id")

    return {
        "success": True,
        "message": f"Successfully signed in user {email}",
        "data": resp_json
    }

  except (InvalidCredentialsError, InvalidTokenError) as e:
    raise Unauthenticated(str(e)) from e
  except ConnectTimeout as e:
    raise ConnectionTimeout(str(e)) from e
  except ConnectionError as e:
    raise ServiceUnavailable(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.post("/credentials", response_model=SignInWithCredentialsResponseModel)
def sign_in_with_credentials(credentials: SignInWithCredentialsModel):
  """This endpoint will take the user email and password as an input
  and returns an id token and refresh token from the IDP.

  If the user does not exist in the user store a user model will be created.
  """
  try:
    user = get_user_by_email(
        credentials.email, check_firestore_user=AUTH_REQUIRE_FIRESTORE_USER)
    data = {
        "email": credentials.email,
        "password": credentials.password,
        "returnSecureToken": True
    }
    url = f"{IDP_URL}:signInWithPassword?key={FIREBASE_API_KEY}"
    resp = requests.post(url, data, timeout=60)
    resp_json = resp.json()
    Logger.info(resp_json)

    status_code = resp.status_code

    # Check with non-200 status code
    if status_code == 400:
      raise InvalidCredentialsError(resp_json.get("error").get("message"))
    if status_code != 200:
      raise Exception(
          f"Error: {status_code} when signing user in ({credentials.email}): "
          + resp_json.get("error").get("message"))

    if not user:
      user = create_user_in_firestore({
        "user_id": credentials.email,
        "email": credentials.email,
      })
    resp_json["user_id"] = user.user_id
    session = create_session(resp_json["user_id"])
    resp_json["session_id"] = session.get("session_id")

    return {
        "success": True,
        "message": f"Successfully signed in user {credentials.email}",
        "data": resp_json
    }

  except (InvalidCredentialsError, InvalidTokenError) as e:
    raise Unauthenticated(str(e)) from e
  except ConnectTimeout as e:
    raise ConnectionTimeout(str(e)) from e
  except ConnectionError as e:
    raise ServiceUnavailable(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e
