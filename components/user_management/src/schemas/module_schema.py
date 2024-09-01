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
Pydantic Model for Module API's
"""
from typing import List, Optional
from pydantic import ConfigDict, BaseModel
from schemas.schema_examples import (BASIC_MODULE_MODEL_EXAMPLE,
                                     FULL_MODULE_MODEL_EXAMPLE)


class BasicModuleModel(BaseModel):
  """Module Skeleton Pydantic Model"""
  # uuid: str
  name: str
  description: str
  actions: list


class FullModuleDataModel(BasicModuleModel):
  """Module Model with uuid, created and updated time"""
  uuid: str
  created_time: str
  last_modified_time: str


class ModuleModel(BasicModuleModel):
  """Module Input Pydantic Model"""
  model_config = ConfigDict(from_attributes=True, extra="forbid", json_schema_extra={"example": BASIC_MODULE_MODEL_EXAMPLE})


class UpdateModuleModel(BaseModel):
  """Update Module Pydantic Request Model"""
  name: Optional[str] = None
  description: Optional[str] = None
  actions: Optional[list] = None
  model_config = ConfigDict(from_attributes=True, extra="forbid", json_schema_extra={"example": BASIC_MODULE_MODEL_EXAMPLE})


class GetModuleResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched the module"
  data: Optional[FullModuleDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched the module",
          "data": FULL_MODULE_MODEL_EXAMPLE
      }
  })


class PostModuleResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the module"
  data: FullModuleDataModel
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the module",
          "data": FULL_MODULE_MODEL_EXAMPLE
      }
  })


class UpdateModuleResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully updated the module"
  data: Optional[FullModuleDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully updated the module",
          "data": FULL_MODULE_MODEL_EXAMPLE
      }
  })


class DeleteModule(BaseModel):
  """Delete Module Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the module"
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully deleted the module"
      }
  })


class AllModuleResponseModel(BaseModel):
  """Module Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Data fetched successfully"
  data: Optional[List[FullModuleDataModel]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Data fetched successfully",
          "data": [FULL_MODULE_MODEL_EXAMPLE]
      }
  })


class ModuleImportJsonResponse(BaseModel):
  """Module Import Json Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the modules"
  data: Optional[List[str]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the modules",
          "data": [
              "44qxEpc35pVMb6AkZGbi", "00MPqUhCbyPe1BcevQDr",
              "lQRzcrRuDpJ9IoW8bCHu"
          ]
      }
  })
