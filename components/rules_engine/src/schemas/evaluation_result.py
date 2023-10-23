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

"""Pydantic Model for Rules evaluation result"""

from pydantic import BaseModel
from typing import Optional

class EvaluationResultSchema(BaseModel):
  """EvaluationResult Pydantic Model"""

  # This is the reference API spec for Rule data model.
  rules_runner: str
  status: str
  result: Optional[dict]
  message: Optional[str]

  class Config:
    orm_mode = True
    schema_extra = {
      "example": {
        "rules_runner": "gorules",
        "message": "Rules evaluation finished.",
        "status": "Success",
        "result": {
          "sample": "test"
        }
      }
    }
