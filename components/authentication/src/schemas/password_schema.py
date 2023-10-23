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
Pydantic Model for Password related API's
"""
from typing import Optional
from pydantic import BaseModel
from schemas.schema_examples import (
    SEND_PASSWORD_RESET_EMAIL_EXAMPLE,
    IDP_SEND_PASSWORD_RESET_EMAIL_RESPONSE_EXAMPLE,
    CHANGE_PASSWORD_RESPONSE_EXAMPLE, RESET_PASSWORD_RESPONSE_EXAMPLE,
    RESET_PASSWORD_EXAMPLE, CHANGE_PASSWORD_EXAMPLE)

# pylint: disable=invalid-name


class SendPasswordResetEmailModel(BaseModel):
  """Send Password Reset Email Pydantic Model"""
  email: str

  class Config:
    orm_mode = True
    schema_extra = {"example": SEND_PASSWORD_RESET_EMAIL_EXAMPLE}


class IDPSendPasswordResetEmailResponseModel(BaseModel):
  """IDP Response model for send password reset email"""
  kind: str
  email: str


class SendPasswordResetEmailResponseModel(BaseModel):
  """Send Password Reset Email Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Data fetched successfully"
  data: IDPSendPasswordResetEmailResponseModel

  class Config:
    orm_mode = True
    schema_extra = {"example": IDP_SEND_PASSWORD_RESET_EMAIL_RESPONSE_EXAMPLE}


class ResetPasswordModel(BaseModel):
  """Reset Password Pydantic Model"""
  oobCode: str
  newPassword: str

  class Config:
    orm_mode = True
    schema_extra = {"example": RESET_PASSWORD_EXAMPLE}


class IDPResetPasswordResponseModel(BaseModel):
  """IDP Response model for send password reset email"""
  kind: str
  email: str
  requestType: str


class ResetPasswordResponseModel(BaseModel):
  """Reset Password Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Data fetched successfully"
  data: IDPResetPasswordResponseModel

  class Config:
    orm_mode = True
    schema_extra = {"example": RESET_PASSWORD_RESPONSE_EXAMPLE}


class ChangePasswordModel(BaseModel):
  """Reset Password Pydantic Model"""
  password: str

  class Config:
    orm_mode = True
    schema_extra = {"example": CHANGE_PASSWORD_EXAMPLE}


class IDPChangePasswordResponseModel(BaseModel):
  """IDP Response model for send password reset email"""
  kind: str
  email: str
  idToken: str
  refreshToken: str
  expiresIn: str


class ChangePasswordResponseModel(BaseModel):
  """Reset Password Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Data fetched successfully"
  data: IDPChangePasswordResponseModel

  class Config:
    orm_mode = True
    schema_extra = {"example": CHANGE_PASSWORD_RESPONSE_EXAMPLE}
