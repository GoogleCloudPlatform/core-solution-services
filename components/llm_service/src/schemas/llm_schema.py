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
from fastapi import UploadFile
from typing import List, Optional
from typing_extensions import TypedDict
from pydantic import ConfigDict, BaseModel
from schemas.schema_examples import (LLM_GENERATE_EXAMPLE,
                                   LLM_MULTIMODAL_GENERATE_EXAMPLE,
                                   QUERY_EXAMPLE,
                                   QUERY_ENGINE_BUILD_EXAMPLE,
                                   QUERY_ENGINE_UPDATE_EXAMPLE,
                                   QUERY_RETRIEVE_EXAMPLE,
                                   QUERY_ENGINE_EXAMPLE,
                                   LLM_EMBEDDINGS_EXAMPLE,
                                   LLM_MULTIMODAL_EMBEDDINGS_EXAMPLE)

class ChatModel(BaseModel):
  id: Optional[str] = None
  user_id: str
  llm_type: str
  title: Optional[str] = ""
  history: Optional[List[dict]] = []
  created_time: str
  last_modified_time: str


class ChatUpdateModel(BaseModel):
  """Model for updating chat properties"""
  title: Optional[str] = None
  history: Optional[List[dict]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "title": "Updated Chat Title",
      "history": [
        {"human": "What is machine learning?"},
        {"ai": "Machine learning is a branch of ai..."}
      ]
    }
  })

class UserQueryUpdateModel(BaseModel):
  title: str

class ModelDetails(BaseModel):
  """Model for LLM details"""
  id: str
  name: str
  description: str
  capabilities: List[str]
  date_added: str
  is_multi: Optional[bool] = False
  model_params: Optional[dict] = None

class LLMGetTypesResponse(BaseModel):
  """Response model for LLM type lists"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved llm types"
  data: Optional[List[str]] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully retrieved llm types",
      "data": ["VertexAI-Chat", "OpenAI-GPT4", "Anthropic-Claude"]
    }
  })

class LLMGetDetailsResponse(BaseModel):
  """Response model for detailed LLM information"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved llm details"
  data: Optional[List[ModelDetails]] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully retrieved llm details", 
      "data": [{
        "id": "VertexAI-Chat",
        "name": "Vertex AI Chat",
        "description": "Latest Gemini model optimized for fast responses",
        "capabilities": ["Chat", "Text Generation"],
        "date_added": "2024-03-15",
        "is_multi": True,
        "model_params": {
          "temperature": 0.7,
          "max_tokens": 1000,
          "top_p": 0.9
        }
      }]
    }
  })

class LLMGetVectorStoreTypesResponse(BaseModel):
  """LLM Get vector store types model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved vector store types"
  data: Optional[list[str]] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully retrieved vector store types",
      "data": []
    }
  })

class LLMGetEmbeddingTypesResponse(BaseModel):
  """LLM Get embedding types model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved embedding types"
  data: Optional[list[str]] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully retrieved embedding types",
      "data": []
    }
  })

class LLMGetQueryEnginesResponse(BaseModel):
  """LLM Get types model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved query engine types"
  data: Optional[list[dict]] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully retrieved query engine types",
          "data": []
      }
  })

class LLMGenerateModel(BaseModel):
  """Model for LLM generation request"""
  prompt: str
  llm_type: Optional[str] = None
  stream: Optional[bool] = False
  chat_file_b64: Optional[str] = None
  chat_file_b64_name: Optional[str] = None
  chat_file_url: Optional[str] = None
  tool_names: Optional[str] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": LLM_GENERATE_EXAMPLE
  })

class LLMMultimodalGenerateModel(BaseModel):
  """Model for LLM multimodal generation request"""
  prompt: str
  llm_type: Optional[str] = None
  stream: Optional[bool] = False
  user_file_b64: Optional[str] = None
  user_file_name: Optional[str] = None
  user_file_url: Optional[str] = None
  tool_names: Optional[List[str]] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": LLM_MULTIMODAL_GENERATE_EXAMPLE
  })

class LLMEmbeddingsModel(BaseModel):
  """Model for LLM embeddings request"""
  text: str
  llm_type: Optional[str] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": LLM_EMBEDDINGS_EXAMPLE
  })

class LLMMultimodalEmbeddingsModel(BaseModel):
  """Model for LLM multimodal embeddings request"""
  text: str
  llm_type: Optional[str] = None
  user_file_b64: Optional[str] = None
  user_file_name: Optional[str] = None
  user_file_url: Optional[str] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": LLM_MULTIMODAL_EMBEDDINGS_EXAMPLE
  })

class LLMChatModel(BaseModel):
  """Chat request model"""
  prompt: str
  llm_type: Optional[str] = None
  upload_file: Optional[UploadFile] = None
  file_url: Optional[str] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": LLM_GENERATE_EXAMPLE
  })

class LLMQueryModel(BaseModel):
  """LLM Query model"""
  prompt: str
  llm_type: Optional[str] = None
  run_as_batch_job: Optional[str] = None
  rank_sentences: Optional[str] = None
  query_filter: Optional[str] = None
  chat_mode: Optional[bool] = False
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": QUERY_EXAMPLE
  })

class FileB64(TypedDict):
  name: str
  b64: str

class LLMQueryEngineUpdateModel(BaseModel):
  """LLM Query Engine update model"""
  name: str
  description: str
  read_access_group: Optional[str] = None
  llm_type: Optional[str] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": QUERY_ENGINE_UPDATE_EXAMPLE
  })

class LLMQueryEngineModel(BaseModel):
  """LLM Query Engine model"""
  doc_url: str
  query_engine: str
  description: str
  query_engine_type: Optional[str] = None
  read_access_group: Optional[str] = None
  llm_type: Optional[str] = None
  embedding_type: Optional[str] = None
  vector_store: Optional[str] = None
  params: Optional[dict] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": QUERY_ENGINE_BUILD_EXAMPLE
  })
  # the documents are sent as base64 encoded strings to preserve backwards
  # compatibility of the API, as it was not originally designed to receive
  # files and converting to form data would break backwards compatability
  # TODO: update to use form data
  documents: Optional[list[FileB64]] = None

class LLMQueryEngineResponse(BaseModel):
  """LLM Generate Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved query engine"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully retrieved query engine",
          "data": QUERY_ENGINE_EXAMPLE
      }
  })

class LLMQueryResponse(BaseModel):
  """LLM Query Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully performed query"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully performed query",
          "data": QUERY_RETRIEVE_EXAMPLE
      }
  })

class LLMUserQueryResponse(BaseModel):
  """LLM Retrieve User Query Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved query"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully retrieved query",
          "data": None
      }
  })


class LLMQueryEngineURLResponse(BaseModel):
  """LLM Get Query Engine URL Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved URLs"
  data: List[str] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully retrieved URLs",
      "data": None
    }
  })


class LLMUserAllQueriesResponse(BaseModel):
  """LLM Get Queries Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved queries"
  data: List[dict] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully retrieved queries",
          "data": None
      }
  })


class LLMGenerateResponse(BaseModel):
  """LLM Generate Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully generated text"
  content: Optional[str] = ""
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully generated text",
          "content": None
      }
  })

class LLMEmbeddingsResponse(BaseModel):
  """LLM Embeddings Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully generated embeddings"
  data: Optional[List[float]] = []
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully generated embeddings",
          "data": None
      }
  })

class LLMMultimodalEmbeddingsResponse(BaseModel):
  """LLM Multimodal Embeddings Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully generated multimodal embeddings"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully generated multimodal embeddings",
          "data": None
      }
  })

class LLMUserChatResponse(BaseModel):
  """LLM User Create Chat Response model"""
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created chat"
  data: Optional[dict] = {}
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully created chat",
      "data": None
    }
  })

class LLMUserAllChatsResponse(BaseModel):
  """LLM Get User All Chats Response model"""
  data: List[dict] = []
  success: Optional[bool] = True
  message: Optional[str] = "Successfully retrieved user chats"
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example": {
      "success": True,
      "message": "Successfully retrieved chats",
      "data": None
    }
  })
