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
Pydantic Models for Inspace Token API's
"""
from pydantic import ConfigDict, BaseModel
from schemas.schema_examples import INSPACE_TOKEN_EXAMPLE


class TokenResponseModel(BaseModel):
  """Response token Skeleton Pydantic Model"""
  token: dict


class InspaceTokenModel(BaseModel):
  """token Skeleton Pydantic Model"""
  success: bool = True
  message: str = "Successfully fetched the inspace token"
  data: dict
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully fetched the inspace token",
      "data": INSPACE_TOKEN_EXAMPLE
    }
  })
