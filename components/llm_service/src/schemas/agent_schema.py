# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Pydantic Model for LLM Agent API's
"""
from pydantic import BaseModel
from schemas.schema_examples import (AGENT_RUN_EXAMPLE,
                                     AGENT_RUN_RESPONSE_EXAMPLE,
                                     AGENT_PLAN_EXAMPLE,
                                     AGENT_PLAN_RESPONSE_EXAMPLE,
                                     USER_PLAN_RESPONSE_EXAMPLE)

class LLMAgentGetAllResponse(BaseModel):
  """Agent Get all model"""
  success: bool = True
  message: str = "Successfully retrieved agents"
  data: dict = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved agents",
            "data": {}
        }
    }

class LLMAgentGetTypeResponse(BaseModel):
  """Agent Get all model"""
  success: bool = True
  message: str = "Successfully retrieved agents"
  data: dict = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved agents",
            "data": {}
        }
    }

class LLMAgentRunModel(BaseModel):
  """LLM Agent run model"""
  prompt: str
  chat_id: str = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": AGENT_RUN_EXAMPLE
    }


class LLMAgentRunResponse(BaseModel):
  """LLM Agent run response model"""
  success: str
  message: str
  data: dict = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": AGENT_RUN_RESPONSE_EXAMPLE
    }

class LLMAgentPlanModel(BaseModel):
  """LLM Agent plan model"""
  prompt: str

  class Config():
    orm_mode = True
    schema_extra = {
        "example": AGENT_PLAN_EXAMPLE
    }

class LLMAgentPlanResponse(BaseModel):
  """LLM Agent plan response model"""
  success: str
  message: str
  data: dict = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": AGENT_PLAN_RESPONSE_EXAMPLE
    }


class LLMAgentPlanRunResponse(BaseModel):
  """LLM Agent plan response model"""
  success: str
  message: str = ""
  data: dict = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": AGENT_PLAN_RESPONSE_EXAMPLE
    }

class LLMUserPlanResponse(BaseModel):
  """LLM User plan response model"""
  success: str
  message: str
  data: dict = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": USER_PLAN_RESPONSE_EXAMPLE
    }
