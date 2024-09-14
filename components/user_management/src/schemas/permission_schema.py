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
Pydantic Model for Permission API's
"""
from typing import List, Optional, Union
from pydantic import ConfigDict, BaseModel
from schemas.schema_examples import (FULL_PERMISSION_MODEL_EXAMPLE,
                                     PERMISSION_FILTER_UNIQUE_EXAMPLE,
                                     POST_PERMISSION_MODEL_EXAMPLE)


class BasicPermissionModel(BaseModel):
  """Permission Skeleton Pydantic Model"""
  name: str
  description: str
  application_id: Optional[Union[str, dict]] = None
  module_id: Union[str, dict]
  action_id: Union[str, dict]
  user_groups: Optional[list] = None


class FullPermissionDataModel(BasicPermissionModel):
  """Permission Model with uuid, created and updated time"""
  uuid: str
  created_time: str
  last_modified_time: str


class GenericInfoDataModel(BaseModel):
  """Basic Description Data Model"""
  uuid: str
  name: str
  description: str

class ActionInfoModel(BaseModel):
  """Basic Description Data Model"""
  uuid: str
  name: str
  description: str
  action_type: str


class AllPermissionsDataModel(BaseModel):
  """All Permissions Pydantic Model"""
  name: str
  description: str
  application_id: Optional[Union[str, GenericInfoDataModel]] = None
  module_id: Union[str, GenericInfoDataModel]
  action_id: Union[str, ActionInfoModel]
  user_groups: Optional[List[Union[str, GenericInfoDataModel]]] = None
  uuid: str
  created_time: str
  last_modified_time: str


class PermissionModel(BaseModel):
  """Permission Input Pydantic Model"""
  name: str
  description: str
  application_id: str
  module_id: str
  action_id: str
  model_config = ConfigDict(
      from_attributes=True,
      extra="forbid",
      json_schema_extra={"example": POST_PERMISSION_MODEL_EXAMPLE}
  )


class UpdatePermissionModel(BaseModel):
  """Update Permission Pydantic Request Model"""
  name: Optional[str] = None
  description: Optional[str] = None
  model_config = ConfigDict(
    from_attributes=True,
    extra="forbid",
    json_schema_extra={
      "example": {
        "name": "assessment_authoring.summative_assessment.edit",
        "description": "edit permission"
      }
    }
  )


class GetPermissionResponseModel(BaseModel):
  """Permission Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched the permission"
  data: Optional[FullPermissionDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched the permission",
          "data": FULL_PERMISSION_MODEL_EXAMPLE
      }
  })


class PostPermissionResponseModel(BaseModel):
  """Permission Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the permission"
  data: FullPermissionDataModel
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the permission",
          "data": FULL_PERMISSION_MODEL_EXAMPLE
      }
  })


class UpdatePermissionResponseModel(BaseModel):
  """Permission Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully updated the permission"
  data: Optional[FullPermissionDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully updated the permission",
          "data": FULL_PERMISSION_MODEL_EXAMPLE
      }
  })


class DeletePermission(BaseModel):
  """Delete Permission Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the permission"
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully deleted the permission"
      }
  })


class AllPermissionResponseModel(BaseModel):
  """Permission Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Data fetched successfully"
  data: Optional[List[AllPermissionsDataModel]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Data fetched successfully",
          "data": [FULL_PERMISSION_MODEL_EXAMPLE]
      }
  })


class PermissionImportJsonResponse(BaseModel):
  """Permission Import Json Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the permissions"
  data: Optional[List[str]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the permissions",
          "data": [
              "44qxEpc35pVMb6AkZGbi", "00MPqUhCbyPe1BcevQDr",
              "lQRzcrRuDpJ9IoW8bCHu"
          ]
      }
  })

class PermissionFilterUniqueData(BaseModel):
  """Unique data fields for competency, result and type of"""
  applications: List[dict] = []
  modules: List[dict] = []
  actions: List[dict] = []
  user_groups: List[dict] = []

class PermissionFilerUniqueResponseModel(BaseModel):
  """Unique values for permission filter Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] ="Successfully fetched the unique values for" + \
      "applications, modules, actions and user_groups."
  data: Optional[PermissionFilterUniqueData] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched the unique values for " + \
                      "applications, modules, actions and user_groups.",
          "data": [PERMISSION_FILTER_UNIQUE_EXAMPLE]
      }
  })
