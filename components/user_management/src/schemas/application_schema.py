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
Pydantic Model for Application API's
"""
from typing import List, Optional
from pydantic import ConfigDict, BaseModel, StrictStr
from common.utils.custom_validator import BaseConfigModel
from schemas.schema_examples import (BASIC_APPLICATION_MODEL_EXAMPLE,
                                     FULL_APPLICATION_MODEL_EXAMPLE)


class BasicApplicationModel(BaseConfigModel):
  """Update Application Pydantic Request Model"""
  name: StrictStr
  description: StrictStr
  modules: list
  model_config = ConfigDict(
      from_attributes=True,
      json_schema_extra={"example": BASIC_APPLICATION_MODEL_EXAMPLE}
  )


class FullApplicationDataModel(BasicApplicationModel):
  """Application Model with uuid, created and updated time"""
  uuid: str
  created_time: str
  last_modified_time: str


class ApplicationModel(BasicApplicationModel):
  """Module Input Pydantic Model"""
  model_config = ConfigDict(
      from_attributes=True,
      extra="forbid",
      json_schema_extra={"example": BASIC_APPLICATION_MODEL_EXAMPLE}
  )


class PostApplicationResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the application"
  data: FullApplicationDataModel
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the application",
          "data": FULL_APPLICATION_MODEL_EXAMPLE
      }
  })


class UpdateApplicationResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully updated the application"
  data: FullApplicationDataModel
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully updated the application",
          "data": FULL_APPLICATION_MODEL_EXAMPLE
      }
  })


class GetApplicationResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched the application"
  data: FullApplicationDataModel
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched the application",
          "data": FULL_APPLICATION_MODEL_EXAMPLE
      }
  })


class DeleteApplicationResponseModel(BaseModel):
  """Delete Module Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the application"
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully deleted the application"
      }
  })


class AllApplicationResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Data fetched successfully"
  data: Optional[List[FullApplicationDataModel]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Data fetched successfully",
          "data": [FULL_APPLICATION_MODEL_EXAMPLE]
      }
  })


class UpdateApplicationModel(BaseModel):
  """Update Module Pydantic Request Model"""
  name: Optional[StrictStr] = None
  description: Optional[StrictStr] = None
  modules: Optional[list] = None
  model_config = ConfigDict(
      from_attributes=True,
      extra="forbid",
      json_schema_extra={"example": BASIC_APPLICATION_MODEL_EXAMPLE}
  )
