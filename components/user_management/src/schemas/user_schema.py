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
Pydantic Model for User API's
"""
import regex
from typing import List, Optional
from typing_extensions import Annotated, Literal
from pydantic import field_validator, StringConstraints, ConfigDict, BaseModel
from common.models.user import USER_TYPES
from schemas.schema_examples import (BASIC_USER_MODEL_EXAMPLE,
                                     FULL_USER_MODEL_EXAMPLE,
                                     UPDATE_USER_MODEL_EXAMPLE,
                                     GET_APPLICATIONS_OF_USER)
class BasicUserModel(BaseModel):
  """User Skeleton Pydantic Model"""
  first_name: str
  last_name: str
  email: Annotated[str, StringConstraints(
      min_length=7,
      max_length=128,
      pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")]
  user_type: Optional[Literal[tuple(USER_TYPES)]] = None
  user_groups: Optional[list] = []
  status: Optional[Literal["active", "inactive"]] = "active"
  is_registered: Optional[bool] = True
  failed_login_attempts_count: Optional[int] = 0
  access_api_docs: Optional[bool] = False
  gaia_id: Optional[str] = ""
  photo_url: Optional[str] = ""

  # pylint: disable=no-self-argument
  @field_validator("first_name")
  @classmethod
  def name_regex(cls,value):
    result = regex.fullmatch(r"[\D\p{L}\p{N}\s]+$", value)
    if len(value)<=60 and result:
      return value
    raise ValueError("Invalid first format")

  @field_validator("last_name")
  @classmethod
  def last_name_regex(cls,value):
    result = regex.fullmatch(r"[\D\p{L}\p{N}\s]+$", value)
    if len(value)<=60 and result:
      return value
    raise ValueError("Invalid last name format")

class InspaceUserModel(BaseModel):
  """Inspace User Model"""
  is_inspace_user: bool = False
  inspace_user_id: str = ""


class FullUserDataModel(BasicUserModel):
  """User Model with user_id, created and updated time"""
  user_id: str
  created_time: str
  last_modified_time: str
  user_type_ref: str
  inspace_user: Optional[InspaceUserModel] = None
  # FIXME: remove optional after all docs get this field
  is_deleted: Optional[bool] = False


class UserModel(BasicUserModel):
  """User Input Pydantic Model"""
  model_config = ConfigDict(
      from_attributes=True,
      extra="forbid",
      json_schema_extra={"example": BASIC_USER_MODEL_EXAMPLE}
  )


class UserSearchResponseModel(BaseModel):
  """User Search Response Pydantic Model"""
  success: bool = True
  message: str = "Successfully fetched the users"
  data: List[FullUserDataModel]
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched the users",
          "data": [FULL_USER_MODEL_EXAMPLE]
      }
  })


class UpdateUserModel(BaseModel):
  """Update User Pydantic Request Model"""
  first_name: Optional[str] = None
  last_name: Optional[str] = None
  user_groups: Optional[list] = None
  access_api_docs: Optional[bool] = None
  gaia_id: Optional[str] = None
  photo_url: Optional[str] = None
  email: Optional[Annotated[str, StringConstraints(
      min_length=7,
      max_length=128,
      pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")]] = None
  # pylint: disable=no-self-argument
  @field_validator("first_name")
  @classmethod
  def first_name_regex(cls,value):
    result = regex.fullmatch(r"[\D\p{L}\p{N}]+$", value)
    if len(value)<=60 and result:
      return value
    raise ValueError("Invalid first name format")
  @field_validator("last_name")
  @classmethod
  def last_name_regex(cls,value):
    result = regex.fullmatch(r"[\D\p{L}\p{N}\s]+$", value)
    if len(value)<=60 and result:
      return value
    raise ValueError("Invalid last name format")
  model_config = ConfigDict(
      from_attributes=True,
      extra="forbid",
      json_schema_extra={"example": UPDATE_USER_MODEL_EXAMPLE}
  )


class UpdateStatusModel(BaseModel):
  """Update User Status Pydantic Request Model"""
  status: Optional[Literal["active", "inactive"]] = None
  model_config = ConfigDict(
      from_attributes=True,
      json_schema_extra={"example": {"status": "active"}}
  )


class GetUserResponseModel(BaseModel):
  """User Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched the user"
  data: Optional[FullUserDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched the user",
          "data": FULL_USER_MODEL_EXAMPLE
      }
  })


class PostUserResponseModel(BaseModel):
  """User Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the user"
  data: FullUserDataModel
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the user",
          "data": FULL_USER_MODEL_EXAMPLE
      }
  })


class BulkImportUserResponseModel(BaseModel):
  """Bulk Import Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the users"
  data: List[str]


class UpdateUserResponseModel(BaseModel):
  """User Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully updated the user"
  data: Optional[FullUserDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully updated the user",
          "data": FULL_USER_MODEL_EXAMPLE
      }
  })


class DeleteUser(BaseModel):
  """Delete User Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = ("Successfully deleted the user and associated"
  " agent, learner/faculty")
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message":
    "Successfully deleted the user and associated agent, learner/faculty"
      }
  })

class TotalCountResponseModel(BaseModel):
  records: Optional[List[FullUserDataModel]] = None
  total_count: int

class AllUserResponseModel(BaseModel):
  """User Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Data fetched successfully"
  data: Optional[TotalCountResponseModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Data fetched successfully",
          "data": {
                    "records":[FULL_USER_MODEL_EXAMPLE],
                    "total_count": 50
                  }
      }
  })


class UserImportJsonResponse(BaseModel):
  """User Import Json Response Pydantic Model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the users"
  data: Optional[List[str]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully created the users",
          "data": [
              "44qxEpc35pVMb6AkZGbi", "00MPqUhCbyPe1BcevQDr",
              "lQRzcrRuDpJ9IoW8bCHu"
          ]
      }
  })


class ApplicationDetails(BaseModel):
  """Get Applications"""
  application_name: str
  application_id: str

  def __init__(self, **kwargs):
    kwargs["application_name"] = kwargs["name"]
    kwargs["application_id"] = kwargs["uuid"]
    super().__init__(**kwargs)


class UserApplication(BaseModel):
  """User details for application details"""
  applications: List[ApplicationDetails]


class GetApplicationsOfUser(BaseModel):
  """Get Applications Assigned to a User"""
  success: Optional[bool] = True
  message: Optional[
      str] = "Successfully fetched applications assigned to the user"
  data: Optional[UserApplication] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully fetched applications assigned to the user",
          "data": GET_APPLICATIONS_OF_USER
      }
  })
