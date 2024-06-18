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

"""Class and methods for handling validate route."""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer
from firebase_admin.auth import InvalidIdTokenError, ExpiredIdTokenError, get_user

from common.utils.errors import TokenNotFoundError, UnauthorizedUserError
from common.utils.http_exceptions import (BadRequest, InvalidToken,
                                          InternalServerError, Unauthorized)
from common.utils.logging_handler import Logger
from common.utils.user_handler import get_user_by_email
from services.validation_service import validate_token
from schemas.validate_token_schema import ValidateTokenResponseModel
from config import (ERROR_RESPONSES,
                    AUTH_REQUIRE_FIRESTORE_USER,
                    AUTH_EMAIL_DOMAINS_WHITELIST,
                    AUTH_AUTO_CREATE_USERS)

Logger = Logger.get_logger(__file__)

router = APIRouter(
    tags=["Authentication"],
    responses=ERROR_RESPONSES)
auth_scheme = HTTPBearer(auto_error=False)


@router.get(
    "/validate",
    response_model=ValidateTokenResponseModel,
    response_model_exclude_none=True)
def validate_id_token(token: auth_scheme = Depends()):
  """Validates the Token present in Headers
  ### Raises:
  UnauthorizedUserError:
    If user does not exist in firestore <br/>
  InvalidTokenError:
    If the token is invalid or has expired <br/>
  Exception 500:
    Internal Server Error. Raised if something went wrong
  ### Returns:
      ValidateTokenResponseModel: Details related to the token
  """

  try:
    if token is None:
      raise TokenNotFoundError("Token not found")
    token_dict = dict(token)
    token_data = validate_token(token_dict["credentials"])
    user_email = token_data["email"]
    email_domain = user_email.split("@")[1]
    create_if_not_exist = False

    if AUTH_AUTO_CREATE_USERS and email_domain in AUTH_EMAIL_DOMAINS_WHITELIST:
      create_if_not_exist = True
    print(f"create_if_not_exist: {create_if_not_exist}")

    user = get_user_by_email(user_email,
                             check_firestore_user=AUTH_REQUIRE_FIRESTORE_USER,
                             create_if_not_exist=create_if_not_exist)
    if not user:
      Logger.error(f"Unauthorized: User {user_email} not found.")
      raise UnauthorizedUserError(
          f"Unauthorized: User {user_email} not found.")

    Logger.info(f"user: {user.to_dict()}")
    user_fields = user.get_fields(reformat_datetime=True)
    if user_fields.get("status") == "inactive":
      raise UnauthorizedUserError("Unauthorized: User status is inactive.")
    token_data["access_api_docs"] = user_fields.get("access_api_docs", False)
    token_data["user_type"] = user_fields.get("user_type")

    return {
        "success": True,
        "message": "Token validated successfully",
        "data": token_data
    }
  except UnauthorizedUserError as e:
    raise Unauthorized(str(e)) from e
  except TokenNotFoundError as e:
    raise BadRequest(str(e)) from e
  except (InvalidIdTokenError, ExpiredIdTokenError) as err:
    raise InvalidToken(str(err)) from err
  except Exception as e:
    raise InternalServerError(str(e)) from e
