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

"""Pydantic Model for Rule API's"""

from pydantic import ConfigDict, BaseModel


class RuleSchema(BaseModel):
  """Rule Pydantic Model"""

  # This is the reference API spec for Rule data model.
  id: str
  title: str
  description: str
  type: str
  fields: dict
  status: str
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "id": "1234",
      "title": "Rule Title",
      "description": "Rule Description",
      "status": "New"
    }
  })
