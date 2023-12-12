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
Pydantic Model for LLM API's
"""
from typing import List, Optional
from pydantic import BaseModel
from schemas.schema_examples import (LLM_GENERATE_EXAMPLE,
                                     QUERY_EXAMPLE,
                                     QUERY_ENGINE_EXAMPLE,
                                     QUERY_RESULT_EXAMPLE,
                                     LLM_EMBEDDINGS_EXAMPLE)

class ChatModel(BaseModel):
  id: Optional[str] = None
  user_id: str
  llm_type: str
  title: Optional[str] = ""
  history: Optional[List[dict]] = []
  created_time: str
  last_modified_time: str


class ChatUpdateModel(BaseModel):
  title: str

class UserQueryUpdateModel(BaseModel):
  title: str

class LLMGetTypesResponse(BaseModel):
  """LLM Get types model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved llm types"
  data: Optional[list[str]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved llm types",
            "data": []
        }
    }

class LLMGetVectorStoreTypesResponse(BaseModel):
  """LLM Get vector store types model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved vector store types"
  data: Optional[list[str]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved vector store types",
            "data": []
        }
    }

class LLMGetEmbeddingTypesResponse(BaseModel):
  """LLM Get embedding types model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved embedding types"
  data: Optional[list[str]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved embedding types",
            "data": []
        }
    }


class LLMGetQueryEnginesResponse(BaseModel):
  """LLM Get types model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved query engine types"
  data: Optional[list[dict]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved query engine types",
            "data": []
        }
    }

class LLMGenerateModel(BaseModel):
  """LLM Generate request model"""
  prompt: str
  llm_type: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": LLM_GENERATE_EXAMPLE
    }

class LLMEmbeddingsModel(BaseModel):
  """LLM Embeddings request model"""
  text: str
  embedding_type: Optional[str] = None

  class Config():
    orm_mode = True
    schema_extra = {
        "example": LLM_EMBEDDINGS_EXAMPLE
    }


class LLMQueryModel(BaseModel):
  """LLM Query model"""
  prompt: str
  llm_type: Optional[str]
  sentence_references: Optional[bool]

  class Config():
    orm_mode = True
    schema_extra = {
        "example": QUERY_EXAMPLE
    }


class LLMQueryEngineModel(BaseModel):
  """LLM Query Engine model"""
  doc_url: str
  query_engine: str
  description: str
  llm_type: Optional[str]
  embedding_type: Optional[str]
  vector_store: Optional[str]
  is_public: Optional[bool]

  class Config():
    orm_mode = True
    schema_extra = {
        "example": QUERY_ENGINE_EXAMPLE
    }


class LLMQueryEngineResponse(BaseModel):
  """LLM Generate Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully generated text"
  data: Optional[str] = ""

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully generated text",
            "data": None
        }
    }

class LLMQueryResponse(BaseModel):
  """LLM Query Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully performed query"
  data: Optional[dict] = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully performed query",
            "data": QUERY_RESULT_EXAMPLE
        }
    }

class LLMUserQueryResponse(BaseModel):
  """LLM Retrieve User Query Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved query"
  data: Optional[dict] = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved query",
            "data": None
        }
    }


class LLMQueryEngineURLResponse(BaseModel):
  """LLM Get Query Engine URL Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved URLs"
  data: List[str] = []

  class Config():
    orm_mode = True
    schema_extra = {
      "example": {
        "success": True,
        "message": "Successfully retrieved URLs",
        "data": None
      }
    }


class LLMUserAllQueriesResponse(BaseModel):
  """LLM Get Queries Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved queries"
  data: List[dict] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved queries",
            "data": None
        }
    }


class LLMGenerateResponse(BaseModel):
  """LLM Generate Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully generated text"
  content: Optional[str] = ""

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully generated text",
            "content": None
        }
    }

class LLMEmbeddingsResponse(BaseModel):
  """LLM Embeddings Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully generated embeddings"
  data: Optional[List[float]] = []

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully generated text",
            "data": None
        }
    }

class LLMUserChatResponse(BaseModel):
  """LLM User Create Chat Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created chat"
  data: Optional[dict] = {}

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully created chat",
            "data": None
        }
    }

class LLMUserAllChatsResponse(BaseModel):
  """LLM Get User All Chats Response model"""
  data: List[dict] = []
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved user chats"

  class Config():
    orm_mode = True
    schema_extra = {
        "example": {
            "success": True,
            "message": "Successfully retrieved chats",
            "data": None
        }
    }
