# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable = consider-using-f-string,logging-fstring-interpolation

"""Firebase token validation"""
import json
import requests
import firebase_admin
from firebase_admin.auth import get_user
from fastapi import Depends
from fastapi.security import HTTPBearer
from common.utils.errors import InvalidTokenError
from common.config import SERVICES
from common.utils.errors import TokenNotFoundError
from common.utils.http_exceptions import (InternalServerError, Unauthenticated)
from common.utils.logging_handler import Logger

auth_scheme = HTTPBearer(auto_error=False)
AUTH_SERVICE_NAME = SERVICES["authentication"]["host"]

default_firebase_app = firebase_admin.initialize_app()

Logger = Logger.get_logger(__file__)

def validate_token(token: auth_scheme = Depends()):
  """
  Main validation function that is depended on by all microservices.
  """
  try:
    user_data = validate_oauth_token(token)
    if not user_data:
      user_data = validate_service_account_token(token)

    if not user_data:
      raise InvalidTokenError("Unauthorized: Invalid token.")

    return user_data

  except (InvalidTokenError, TokenNotFoundError) as e:
    raise Unauthenticated(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e


def validate_oauth_token(token: auth_scheme = Depends()):
  """
  Validate OAuth token from Firebase Auth or Cloud Identity Platform.
  """
  if not token:
    raise TokenNotFoundError("Unauthorized: token is empty.")

  token_dict = dict(token)
  if token_dict["credentials"]:
    api_endpoint = f"http://{AUTH_SERVICE_NAME}/{AUTH_SERVICE_NAME}/" \
        "api/v1/validate"
    res = requests.get(
        url=api_endpoint,
        headers={
            "Content-Type": "application/json",
            "Authorization":
                f"{token_dict['scheme']} {token_dict['credentials']}"
        },
        timeout=60)
    data = res.json()
    if res.status_code == 200 and data["success"] is True:
      return data.get("data")
    else:
      raise InvalidTokenError(data["message"])
  else:
    raise InvalidTokenError("Unauthorized: Invalid token.")


def validate_service_account_token(token: auth_scheme = Depends()):
  """
  Validate token for Service Account.
  """
  if not token:
    raise InvalidTokenError("Unauthorized: token is empty.")

  # TODO: Implement authentication with Service Account.
  print(token)
  return False


def validate_user_type_and_token(accepted_user_types: list,
                                 token: auth_scheme = Depends()):
  """_summary_

  Args:
      accepted_user_types
      token (auth_scheme, optional): _description_. Defaults to Depends().

  Raises:
      InvalidTokenError: _description_
      Unauthenticated: _description_
      InternalServerError: _description_

  Returns:
      Boolean: token is valid or not
  """
  try:
    if token is None:
      raise InvalidTokenError("Unauthorized: token is empty.")
    token_dict = dict(token)
    if token_dict["credentials"]:
      api_endpoint = f"http://{AUTH_SERVICE_NAME}/{AUTH_SERVICE_NAME}" \
          "/api/v1/validate_token"
      res = requests.get(
          url=api_endpoint,
          headers={
              "Content-Type":
                  "application/json",
              "Authorization":
                  f"{token_dict['scheme']} {token_dict['credentials']}"
          },
          timeout=60)
      data = res.json()
      if (res.status_code == 200 and data["success"] is True and
          data["data"]["user_type"] in accepted_user_types):
        return data.get("data")
      else:
        raise InvalidTokenError(data["message"])
    else:
      raise InvalidTokenError("Unauthorized")
  except InvalidTokenError as e:
    raise Unauthenticated(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e


def validate_user(token: auth_scheme = Depends()):
  return validate_user_type_and_token(token)


def user_verification(token: str) -> json:
  """
  Verify the user with firebase IDToken
  :param token:
  :return: json
  """
  host = SERVICES["authentication"]["host"]
  port = SERVICES["authentication"]["port"]
  api_endpoint = f"http://{host}:{port}/authentication/api/v1/validate"
  response = requests.get(
      url=api_endpoint,
      headers={
          "Content-Type": "application/json",
          "Authorization": token
      },
      timeout=10)

  return response

def create_authz_filter(user_data: dict):
  """
  Create authorization filter based on roles in user data.
  
  Args:
    user_data: dict of user data from auth token
  
  Returns:
    dict containing authorization filter
  """
  authz_filter = None

  if user_data:
    # get firebase user
    Logger.info(f"user_data: {user_data}")
    user = get_user(user_data["user_id"])
    Logger.info(f"user: {user}")

    # get roles
    roles = None
    if user.custom_claims and "roles" in user.custom_claims:
      roles = user.custom_claims["roles"]
      Logger.info(f"roles: {roles} from user.custom_claims")

    Logger.info(
        f"firebase ID token for {user_data['user_id']} has roles {roles}")
    # TODO: change this later to accomodate more than one
    if roles:
      authz_filter = {"authz": {"contains": roles[0]}}
    else:
      authz_filter = None

  return authz_filter

def get_roles_from_custom_claims(user_data: dict):
  """
  Get roles from custom claims for authorization filter.
  
  Args:
    user_data: dict of user data from auth token
  
  Returns:
    dict containing roles and performs as a authorization filter
  """
  role_claims_dict = None

  if user_data:
    # get firebase user
    Logger.info(f"user_data: {user_data}")
    user = get_user(user_data["user_id"])
    Logger.info(f"user: {user}")

    # get roles
    roles = None
    if user.custom_claims and "roles" in user.custom_claims:
      roles = user.custom_claims["roles"]
      Logger.info(f"roles: {roles} from user.custom_claims")

    Logger.info(
        f"firebase ID token for {user_data['user_id']} has roles: {roles}")

    if roles:
      role_claims_dict = {"roles": list(roles)}
    else:
      role_claims_dict = None

  return role_claims_dict
