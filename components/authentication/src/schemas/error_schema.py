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
Pydantic models for different status codes
"""
from typing import Optional
from pydantic import ConfigDict, BaseModel


class NotFoundErrorResponseModel(BaseModel):
  success: bool = False
  message: Optional[str] = None
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": False,
          "message": "Resource with uuid o1nv13n6sbu0ny not found",
          "data": {}
      }
  })


class InternalServerErrorResponseModel(BaseModel):
  success: bool = False
  message: Optional[str] = "Internal Server Error"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": False,
          "message": "Internal server error",
          "data": {}
      }
  })


class ValidationErrorResponseModel(BaseModel):
  success: bool = False
  message: Optional[str] = "Validation Failed"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": False,
          "message": "Validation Failed",
          "data": []
      }
  })


class UnauthorizedUserErrorResponseModel(BaseModel):
  success: bool = False
  message: Optional[str] = "User is not authorized"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": False,
          "message": "User is not authorized",
          "data": []
      }
  })


class ConnectionTimeoutErrorResponseModel(BaseModel):
  success: bool = False
  message: Optional[str] = "Request Timed-out"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": False,
          "message": "Request Timed-out",
          "data": {}
      }
  })


class ConnectionErrorResponseModel(BaseModel):
  success: bool = False
  message: Optional[str] = "Connection Error"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": False,
          "message": "Connection Error",
          "data": {}
      }
  })
