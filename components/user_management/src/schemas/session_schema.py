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
Pydantic Model for Learner Profile API's
"""

from typing import Optional, List
from typing_extensions import Literal
from pydantic import ConfigDict, BaseModel
from schemas.schema_examples import (POST_SESSION_EXAMPLE, FULL_SESSION_EXAMPLE,
                                     UPDATE_SESSION_EXAMPLE)

NODES = Literal["assessments", "learning_resources"]


class BasicSessionModel(BaseModel):
  """Session Skeleton Pydantic Model"""
  user_id: str
  parent_session_id: Optional[str] = None
  session_data: Optional[dict] = None
  is_expired: Optional[bool] = False


class FullSessionDataModel(BasicSessionModel):
  """Session Skeleton Model with session_id, created and updated time"""
  session_id: str
  created_time: str
  last_modified_time: str


class PostSessionModel(BasicSessionModel):
  """Session Pydantic Model"""
  model_config = ConfigDict(from_attributes=True, extra="forbid", json_schema_extra={"example": POST_SESSION_EXAMPLE})


class UpdateSessionModel(BaseModel):
  """Update Session Pydantic Model"""
  session_data: Optional[dict] = {}
  is_expired: Optional[bool] = None
  model_config = ConfigDict(from_attributes=True, extra="forbid", json_schema_extra={"example": UPDATE_SESSION_EXAMPLE})


class GetSessionResponseModel(BaseModel):
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched the session"
  data: Optional[FullSessionDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully fetched the session",
      "data": FULL_SESSION_EXAMPLE
    }
  })


class GetAllSessionResponseModel(BaseModel):
  success: Optional[bool] = True
  message: Optional[str] = "Successfully fetched the session"
  data: Optional[List[FullSessionDataModel]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully fetched the session",
      "data": [FULL_SESSION_EXAMPLE]
    }
  })


class PostSessionResponseModel(BaseModel):
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created the session"
  data: Optional[FullSessionDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully created the session",
      "data": FULL_SESSION_EXAMPLE
    }
  })


class UpdateSessionResponseModel(BaseModel):
  success: Optional[bool] = True
  message: Optional[str] = "Successfully updated the session"
  data: Optional[FullSessionDataModel] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully updated the session",
      "data": FULL_SESSION_EXAMPLE
    }
  })
