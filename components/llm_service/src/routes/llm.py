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

# pylint: disable = broad-except

""" LLM endpoints """
from fastapi import APIRouter

from common.utils.errors import (PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest)
from config import (PAYLOAD_FILE_SIZE,
                    ERROR_RESPONSES, LLM_TYPES, EMBEDDING_MODELS)
from schemas.llm_schema import (LLMGenerateModel,
                                LLMGetTypesResponse,
                                LLMGetEmbeddingTypesResponse,
                                LLMGenerateResponse)
from services.llm_generate import llm_generate

router = APIRouter(prefix="/llm", tags=["LLMs"], responses=ERROR_RESPONSES)


@router.get(
    "",
    name="Get all LLM types",
    response_model=LLMGetTypesResponse)
def get_llm_list():
  """
  Get available LLMs

  Returns:
      LLMGetResponse
  """
  try:
    return {
      "success": True,
      "message": "Successfully retrieved llm types",
      "data": LLM_TYPES
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.get(
    "/embedding",
    name="Get supported embedding types",
    response_model=LLMGetEmbeddingTypesResponse)
def get_embedding_list():
  """
  Get supported embedding types

  Returns:
      LLMGetEmbeddingTypesResponse
  """
  embeddings = EMBEDDING_MODELS
  try:
    return {
      "success": True,
      "message": "Successfully retrieved embedding types",
      "data": embeddings
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.post(
    "/generate",
    name="Generate text from LLM",
    response_model=LLMGenerateResponse)
async def generate(gen_config: LLMGenerateModel):
  """
  Generate text with an LLM

  Args:
      gen_config: Input config dictionary,
        including prompt(str) and llm_type(str) type for model

  Returns:
      LLMGenerateResponse
  """
  genconfig_dict = {**gen_config.dict()}

  prompt = genconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  llm_type = genconfig_dict.get("llm_type")

  try:
    result = await llm_generate(prompt, llm_type)

    return {
        "success": True,
        "message": "Successfully generated text",
        "content": result
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


