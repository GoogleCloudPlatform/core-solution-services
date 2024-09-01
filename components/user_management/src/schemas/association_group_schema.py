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
Pydantic Model for Group Association API's
"""
from typing import List, Optional
from typing_extensions import Literal
from pydantic import ConfigDict, BaseModel
from config import IMMUTABLE_ASSOCIATION_GROUPS
from schemas.schema_examples import (ASSOCIATION_GROUP_EXAMPLE,
                                     BASIC_ASSOCIATION_GROUP_EXAMPLE,
                                     FULL_USER_MODEL_EXAMPLE)
from schemas.user_schema import FullUserDataModel

# pylint: disable=invalid-name
ALLOWED_IMMUTABLE_ASSOCIATION_GROUPS = \
  Literal[tuple(IMMUTABLE_ASSOCIATION_GROUPS)]

class BasicAssociationGroupModel(BaseModel):
  """Association Group Skeleton Pydantic Model"""
  name: str
  description: str


class ImmutableAssociationGroupModel(BasicAssociationGroupModel):
  """Immutable Association Group Pydantic Model"""
  name: ALLOWED_IMMUTABLE_ASSOCIATION_GROUPS
  model_config = ConfigDict(from_attributes=True, extra="forbid", json_schema_extra={"example": BASIC_ASSOCIATION_GROUP_EXAMPLE})


class FullAssociationGroupDataModel(BasicAssociationGroupModel):
  """Association Group Model with uuid, created and updated time"""
  uuid: str
  association_type: str
  created_time: str
  last_modified_time: str
  is_immutable: Optional[bool] = False


class PostImmutableAssociationGroupResponseModel(BaseModel):
  """Post Immutable Association Response Model"""
  success: bool = True
  message: str = "Successfully created the association group"
  data: FullAssociationGroupDataModel
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the association group",
          "data": ASSOCIATION_GROUP_EXAMPLE
      }
  })


class GetAssociationGroupResponseModel(BaseModel):
  """Fetch Association Group Response Pydantic Model"""
  success: bool = True
  message: str = "Successfully fetched the association group"
  data: List[FullAssociationGroupDataModel]
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched the association group",
          "data": [ASSOCIATION_GROUP_EXAMPLE]
      }
  })

class GetAllAssociationGroupResponseModel(BaseModel):
  """Fetch Association Group Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched the association group"
  data: Optional[List[FullAssociationGroupDataModel]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={"example": ASSOCIATION_GROUP_EXAMPLE})

class AutoUpdateAllAssociationGroups(BaseModel):
  """Node Skeleton Pydantic Model"""
  uuid: str
  alias: Literal["discipline"]
  name: Optional[str] = None

class AutoUpdateAllAssociationGroupDisciplines(BaseModel):
  """Disciplines Request Pydantic Model"""
  program_id: str
  disciplines: List[AutoUpdateAllAssociationGroups]

class AutoUpdateAllAssociationGroupsResponseModel(BaseModel):
  """AutoUpdateAllAssociationGroups Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = \
    "Successfully updated the following association groups"
  data: Optional[list] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully updated the association group",
          "data": []
      }
  })

class UserTypeResponseModel(BaseModel):
  """Get list of Users for given UserType"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched users "\
              "that can be added to association group"
  data: Optional[List[FullUserDataModel]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched users "\
              "that can be added to association group",
          "data": [FULL_USER_MODEL_EXAMPLE]
      }
  })
