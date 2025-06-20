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

"""Class and methods for handling generate route."""

from services.refresh_token_service import generate_token
from services.validation_service import validate_token
from utils.exception_handler import InvalidRefreshTokenError
from fastapi import APIRouter
from schemas.generate_token_schema import (GenerateTokenResponseModel,
                                           GenerateTokenRequestModel)
from common.utils.http_exceptions import (InvalidToken, InternalServerError)
from common.utils.logging_handler import Logger
from common.utils.sanitization_service import sanitize_token_data
from common.models import User
from config import ERROR_RESPONSES
from metrics import track_token_refresh

# pylint: disable = broad-exception-raised
router = APIRouter(
    tags=["RefreshToken"],
    responses=ERROR_RESPONSES)
Logger = Logger.get_logger(__file__)


@router.post("/generate", response_model=GenerateTokenResponseModel)
@track_token_refresh
def generate_id_token(input_params: GenerateTokenRequestModel):
  """Generates IdToken from the Refresh token received

  Args:
      refresh_token(str): refresh token
      input_params(dict): GenerateTokenRequestModel

  Returns:
      GenerateTokenResponseModel: Contains access token, idToken and their
      expiry time.

  Parameters
  ----------
  """
  try:
    input_dict = {**input_params.dict()}
    token_resp = generate_token(input_dict)

    decoded_token = validate_token(token_resp["id_token"])
    Logger.info(f"decoded_token: {sanitize_token_data(decoded_token)}")
    user = User.find_by_email(decoded_token["email"])
    token_resp["user_id"] = user.user_id
    return {
        "success": True,
        "message": "Token generated successfully",
        "data": token_resp
    }
  except InvalidRefreshTokenError as e:
    raise InvalidToken(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e
