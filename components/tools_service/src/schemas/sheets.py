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

"""Pydantic Model for Email's related API's"""

from pydantic import BaseModel

class CreateSheetSchema(BaseModel):
  """Email Pydantic Model"""

  name: str
  columns: list
  rows: list
  share_emails: list

  class Config:
    orm_mode = True
    schema_extra = {
      "example": {
        "name": "Name of the Spreadsheet",
        "columns": ["A", "B"],
        "rows": [[1,2], [3,4]],
        "share_emails": ["test@example.com"]
      }
    }
