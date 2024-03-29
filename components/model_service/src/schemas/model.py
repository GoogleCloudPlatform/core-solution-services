"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Pydantic Model for Model API's
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class ModelSchema(BaseModel):
  """Model Pydantic Model"""

  # This is the reference API spec for Model data model.
  id: str
  title: str
  description: str
  status: str
  created_at: Optional[datetime]
  modified_at: Optional[datetime]

  class Config():
    orm_mode = True
    schema_extra = {
      "example": {
        "id": "1234",
        "title": "Title",
        "description": "Description",
        "status": "New"
      }
    }
