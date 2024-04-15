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
import os.path
import base64
from base64 import b64decode
from fastapi import APIRouter

from common.utils.logging_handler import Logger
from common.utils.errors import (PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest)
from config import (PAYLOAD_FILE_SIZE,
                    ERROR_RESPONSES, get_model_config)
from schemas.llm_schema import (LLMGenerateModel,
                                LLMMultiGenerateModel,
                                LLMGetTypesResponse,
                                LLMGetEmbeddingTypesResponse,
                                LLMGenerateResponse,
                                LLMEmbeddingsResponse,
                                LLMEmbeddingsModel)
from services.llm_generate import llm_generate, llm_generate_multi
from services.embeddings import get_embeddings

router = APIRouter(prefix="/llm", tags=["LLMs"], responses=ERROR_RESPONSES)

Logger = Logger.get_logger(__file__)

@router.get(
    "",
    name="Get all LLM types",
    response_model=LLMGetTypesResponse)
def get_llm_list():
  """
  Get available LLMs

  Returns:
      LLMGetTypesResponse
  """
  try:
    return {
      "success": True,
      "message": "Successfully retrieved llm types",
      "data": get_model_config().get_llm_types()
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.get(
    "/embedding_types",
    name="Get supported embedding types",
    response_model=LLMGetEmbeddingTypesResponse)
def get_embedding_types():
  """
  Get supported embedding types

  Returns:
      LLMGetEmbeddingTypesResponse
  """
  try:
    return {
      "success": True,
      "message": "Successfully retrieved embedding types",
      "data": get_model_config().get_embedding_types()
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e

@router.post(
    "/embedding",
    name="Generate embeddings from LLM",
    response_model=LLMEmbeddingsResponse)
async def generate_embeddings(embeddings_config: LLMEmbeddingsModel):
  """
  Generate embeddings with an LLM

  Args:
      embeddings_config: Input config dictionary,
        including text(str) and embedding_type(str) type for model

  Returns:
      LLMEmbeddingsResponse
  """
  embeddings_config_dict = {**embeddings_config.dict()}
  text = embeddings_config_dict.get("text")
  if text is None or text == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(text) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Text must be less than {PAYLOAD_FILE_SIZE}")

  embedding_type = embeddings_config_dict.get("embedding_type")

  try:
    _, embeddings = get_embeddings(text, embedding_type)

    return {
        "success": True,
        "message": "Successfully generated embeddings",
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

@router.post(
    "/generate/multi",
    name="Generate text with a multimodal LLM",
    response_model=LLMGenerateResponse)
async def generate_multi(gen_config: LLMMultiGenerateModel):
  """
  Generate text with a multimodal LLM

  Args:
      gen_config: Input config dictionary,
        including user_file(UploadFile) prompt(str) 
        and llm_type(str) type for model

  Returns:
      LLMMultiGenerateResponse
  """
  genconfig_dict = {**gen_config.dict()}
  user_file_b64 = genconfig_dict.get("user_file_b64")
  user_file_name = genconfig_dict.get("user_file_name")
  prompt = genconfig_dict.get("prompt")
  llm_type = genconfig_dict.get("llm_type")

  if (user_file_b64 is None or user_file_b64 == "" or
    user_file_name is None or user_file_name == "" or
    prompt is None or prompt == ""):
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  # Make sure that the user file is a valid image or video
  vertex_mime_types = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".mov": "video/mov",
    ".avi": "video/avi",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpg",
    ".wmv": "video/wmv"
  }
  user_file_extension = os.path.splitext(user_file_name)[1]
  user_file_extension = vertex_mime_types.get(user_file_extension)
  if not user_file_extension:
    return BadRequest("File must be a picture or a video.")

  # Make sure that the user file b64 is a valid image or video
  image_signatures = {
      b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
      b"\xFF\xD8\xFF": "jpg",
      b"\xFF\xD8": "jpeg",
      b"\x47\x49\x46\x38": "gif",
      b"\x00\x00\x00 ftyp": "mp4",
      b"\x00\x00\x00\x14": "mov",
      b"RIFF": "avi",
      b"\x00\x00\x01\xba!\x00\x01\x00": "mpeg",
      b"\x00\x00\x01\xB3": "mpg",
      b"0&\xb2u\x8ef\xcf\x11": "wmv"
  }
  file_header = base64.b64decode(user_file_b64)[:8]  # Get the first 8 bytes
  user_file_type = None
  for sig, file_format in image_signatures.items():
    if file_header.startswith(sig):
      user_file_type = file_format
      break
  if not user_file_type:
    return BadRequest("File data must be a picture or a video.")

  try:
    user_file_bytes = b64decode(user_file_b64)
    result = await llm_generate_multi(prompt, user_file_bytes,
                                      user_file_extension, llm_type)

    return {
        "success": True,
        "message": "Successfully generated text",
        "content": result
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e
