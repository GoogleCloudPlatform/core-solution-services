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

class EmailSchema(BaseModel):
  """Email Pydantic Model"""

  recipient: str
  subject: str
  message: str

  class Config:
    orm_mode = True
    schema_extra = {
      "example": {
        "recipient": "test@example.com",
        "subject": "Hello",
        "message": "From the world."
      }
    }
