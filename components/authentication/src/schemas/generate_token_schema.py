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
Pydantic Models for GenerateToken API's
"""
from pydantic import BaseModel
from typing import Optional
from schemas.schema_examples import (BASIC_GENERATE_TOKEN_RESPONSE_EXAMPLE)



class ResponseModel(BaseModel):
  access_token: str
  expires_in: str
  token_type: str
  refresh_token: str
  id_token: str
  project_id: str
  user_id: str


class GenerateTokenResponseModel(BaseModel):
  """Generate Token Response Pydantic Model"""
  success: Optional[bool]
  message: Optional[str]
  data: ResponseModel

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Token validated successfully",
            "data": BASIC_GENERATE_TOKEN_RESPONSE_EXAMPLE
        }
    }


class GenerateTokenRequestModel(BaseModel):
  refresh_token: str

  class Config():
    orm_mode = True
    schema_extra = {"example": {"refresh_token": "Afhfhh...........frtyhgjh"}}
