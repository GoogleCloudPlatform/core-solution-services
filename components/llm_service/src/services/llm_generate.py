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
LLM Generation Service
"""
# pylint: disable=import-outside-toplevel,line-too-long
import time
import requests
import base64
from typing import Optional, List, AsyncGenerator, Union
import google.auth
import google.auth.transport.requests
import google.cloud.aiplatform
from openai import OpenAI, OpenAIError
from vertexai.language_models import (ChatModel, TextGenerationModel)
from vertexai.generative_models import (
    GenerativeModel, Part, GenerationConfig, HarmCategory, HarmBlockThreshold, Content)
from common.config import PROJECT_ID, REGION
from common.models import UserChat, UserQuery
from common.utils.errors import ResourceNotFoundException
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import (post_method,
                                          DEFAULT_TIMEOUT)
from common.utils.token_handler import UserCredentials
from common.utils.context_vars import get_context
from config import (get_model_config, get_provider_models,
                    get_provider_value, get_provider_model_config,
                    get_model_config_value, get_model_system_prompt,
                    PROVIDER_VERTEX, PROVIDER_TRUSS,
                    PROVIDER_MODEL_GARDEN, PROVIDER_VLLM,
                    PROVIDER_LANGCHAIN, PROVIDER_LLM_SERVICE,
                    PROVIDER_ANTHROPIC, KEY_MODEL_REGION,
                    KEY_MODEL_ENDPOINT, KEY_MODEL_NAME,
                    KEY_MODEL_TOKEN_LIMIT,
                    KEY_MODEL_PARAMS, KEY_MODEL_CONTEXT_LENGTH,
                    DEFAULT_LLM_TYPE, DEFAULT_MULTIMODAL_LLM_TYPE,
                    KEY_SUB_PROVIDER, SUB_PROVIDER_OPENAPI,
                    DEFAULT_CHAT_SUMMARY_MODEL)
from services.langchain_service import langchain_llm_generate
from services.query.data_source import DataSourceFile
from utils.errors import ContextWindowExceededException
from utils.file_helper import read_gcs_file_as_base64
from anthropic import AnthropicVertex

Logger = Logger.get_logger(__file__)

# A conservative characters-per-token constant, used to check
# whether prompt length exceeds context window size
CHARS_PER_TOKEN = 3
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
}


async def llm_generate(prompt: str, llm_type: str, stream: bool = False) -> \
    Union[str, AsyncGenerator[str, None]]:
  """
  Generate text with an LLM given a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use (default to openai)
    stream: whether to stream the response
  Returns:
    Either the full text response as str, or an AsyncGenerator yielding response chunks
  """
  context = get_context()
  Logger.info(
    "LLM text generation initiated",
    extra={
      "operation": "llm_generate",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "prompt_length": len(prompt) if prompt else 0,
      "prompt_preview": prompt[:50] + "..." if len(prompt) > 50\
          else prompt if prompt else "",
      "stream": stream,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )
  # default to openai LLM
  if llm_type is None:
    llm_type = DEFAULT_LLM_TYPE

  try:
    start_time = time.time()

    # check whether the context length exceeds the limit for the model
    check_context_length(prompt, llm_type)

    # call the appropriate provider to generate the chat response
    # for Google models, prioritize native client over langchain
    chat_llm_types = get_model_config().get_chat_llm_types()
    if llm_type in get_provider_models(PROVIDER_LLM_SERVICE):
      is_chat = llm_type in chat_llm_types
      response = await llm_service_predict(prompt, is_chat, llm_type)
    elif llm_type in get_provider_models(PROVIDER_TRUSS):
      model_endpoint = get_provider_value(
          PROVIDER_TRUSS, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_truss_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_VLLM):
      model_endpoint = get_provider_value(
          PROVIDER_VLLM, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_vllm_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_MODEL_GARDEN):
      response = await model_garden_predict(prompt, llm_type)
    elif llm_type in get_provider_models(PROVIDER_ANTHROPIC):
      response = await anthropic_predict(prompt, llm_type, stream=stream)
    elif llm_type in get_provider_models(PROVIDER_VERTEX):
      google_llm = get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      if google_llm is None:
        raise RuntimeError(
            f"Vertex model name not found for llm type {llm_type}")
      is_chat = llm_type in chat_llm_types
      is_multimodal = False
      response = await google_llm_predict(
        prompt, is_chat, is_multimodal, google_llm, stream=stream)
    elif llm_type in get_provider_models(PROVIDER_LANGCHAIN):
      response = await langchain_llm_generate(prompt, llm_type)
    else:
      raise ResourceNotFoundException(f"Cannot find llm type '{llm_type}'")

    process_time = round(time.time() - start_time)
    Logger.info(
      "LLM generation latency",
      extra={
        "operation": "llm_generate",
        "metric_type": "llm_generation_latency",
        "llm_type": llm_type,
        "duration_ms": round(process_time * 1000, 2),
        "request_id": context["request_id"],
        "trace": context["trace"],
        "session_id": context["session_id"]
      }
    )
    return response
  except Exception as e:
    raise InternalServerError(str(e)) from e


async def anthropic_predict(prompt: str,
                            llm_type: str,
                            parameters: dict = None,
                            stream: bool = False,
                            user_file_bytes: bytes = None,
                            user_files: List[DataSourceFile] = None,
                            user_chat: Optional[UserChat] = None)\
                              -> Union[str, AsyncGenerator[str, None]]:
  """
  Generate text with anthropic claude sonnet.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use (anthropic claude sonnet)
    parameters: dict of parameters for the model (temperature, top_p, etc.)
    stream: whether to stream the response
    user_file_bytes: bytes of the file provided by the user
    user_files: list of DataSourceFiles for files provided by the user
    user_chat: chat history for context
  Returns:
    Either the full text response as str,
    or an AsyncGenerator yielding response chunks
  """
  context = get_context()
  Logger.info(
    "Anthropic predict initiated",
    extra={
      "operation": "anthropic_predict",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "prompt_length": len(prompt) if prompt else 0,
      "prompt_preview": prompt[:50] + "..." if len(prompt) > 50\
          else prompt if prompt else "",
      "stream": stream,
      "has_user_file_bytes": user_file_bytes is not None,
      "has_user_files": user_files is not None and len(user_files) > 0,
      "with_file": user_file_bytes is not None or (user_files is not None and len(user_files) > 0),
      "chat_id": user_chat.id if user_chat else None,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )

  try:
    region = get_provider_value(PROVIDER_ANTHROPIC,
                                KEY_MODEL_REGION,
                                model_id=None,
                                default="us-east5")

    Logger.info(f"Using Anthropic region: {region} for model: {llm_type}")
    client = AnthropicVertex(project_id=PROJECT_ID, region=region)

    model_name = get_provider_value(PROVIDER_ANTHROPIC,
                                    KEY_MODEL_ENDPOINT,
                                    model_id=llm_type)

    token_limit = get_provider_value(PROVIDER_ANTHROPIC,
                                     KEY_MODEL_TOKEN_LIMIT,
                                     model_id=llm_type)

    if token_limit is None:
      token_limit = 4096

    # Prepare API call parameters
    api_params = {
      "model": model_name,
      "max_tokens": token_limit
    }

    # Add custom parameters if provided
    if parameters:
      allowed_params = ["temperature", "top_p", "top_k", "stop_sequences"]
      for param, value in parameters.items():
        if param in allowed_params:
          api_params[param] = value

    # Build messages array with chat history and current prompt
    messages = []

    # Add chat history if provided
    if user_chat is not None:
      messages.extend(await convert_history_to_anthropic_messages(user_chat.history))

    # Build current message content
    current_message_content = []

    # Add text content
    current_message_content.append({
      "type": "text",
      "text": prompt
    })

    # Handle file attachments with Anthropic-specific validation
    if user_file_bytes is not None and user_files is not None:
      # Handle single file with bytes
      file_info = user_files[0]  # Assuming single file when bytes provided
      if _is_anthropic_supported_image(file_info.mime_type):
        # For Anthropic, we need base64 encoded data
        encoded_data = base64.b64encode(user_file_bytes).decode("utf-8")
        current_message_content.append({
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": file_info.mime_type,
            "data": encoded_data
          }
        })
        Logger.info(f"Added image to Anthropic request: {file_info.mime_type}")
      else:
        Logger.warning(f"Skipping unsupported file\
                        type for Anthropic: {file_info.mime_type}")

    elif user_files is not None:
      # Handle multiple files or files with URIs
      supported_files_count = 0
      for user_file in user_files:
        if _is_anthropic_supported_image(user_file.mime_type):
          if user_file.gcs_path:
            # Read file from GCS path and convert to base64
            try:
              encoded_data = await read_gcs_file_as_base64(user_file.gcs_path)
              current_message_content.append({
                "type": "image",
                "source": {
                  "type": "base64",
                  "media_type": user_file.mime_type,
                  "data": encoded_data
                }
              })
              supported_files_count += 1
              Logger.info(f"Added GCS image to Anthropic request: {user_file.gcs_path}")
            except Exception as e:
              Logger.error(f"Failed to read file from GCS: {e}")
              raise
          else:
            Logger.warning(f"No file content available for: {user_file}")
        else:
          Logger.warning(f"Skipping unsupported file type for Anthropic: {user_file.mime_type}")

      if user_files and supported_files_count == 0:
        Logger.warning("No supported image files found for Anthropic model")

    # Add current message to messages array
    messages.append({
      "role": "user",
      "content": current_message_content
    })

    # Add messages to API parameters
    api_params["messages"] = messages

    if stream:
      # Return an async generator for streaming
      async def stream_response():
        try:
          with client.messages.stream(**api_params) as stream:
            for text in stream.text_stream:
              yield text
        except Exception as e:
          Logger.error(f"Anthropic streaming error: {e}")
          raise e

      return stream_response()
    else:
      # Non-streaming response
      predictions_text = client.messages.create(**api_params)
      return predictions_text.content[0].text

  except Exception as e:
    Logger.error(f"Anthropic predict error: {e}")
    raise e


async def convert_history_to_anthropic_messages(history: list) -> list:
  """
  Convert UserChat history to Anthropic messages format.
  Includes Anthropic-specific file validation and GCS file handling.
  
  Args:
    history: A history entry from a UserChat object
    
  Returns:
    List of properly formatted Anthropic messages
  """
  messages = []

  for entry in history:
    content = UserChat.entry_content(entry)

    if UserChat.is_human(entry):
      # Handle human messages
      message_content = [{"type": "text", "text": content}]
      messages.append({
        "role": "user", 
        "content": message_content
      })

    elif UserChat.is_ai(entry):
      # Handle AI messages
      messages.append({
        "role": "assistant",
        "content": content
      })

    elif UserChat.is_full_query_response(entry):
      # Handle query responses
      converted_content = UserChat.convert_query_response_to_chat_entry(entry)
      messages.append({
        "role": "assistant",
        "content": converted_content
      })

    elif UserChat.is_file_bytes(entry) or UserChat.is_file_uri(entry):
      # Handle file attachments with Anthropic validation
      if messages and messages[-1]["role"] == "user":
        # Add file to existing user message if supported
        if UserChat.is_file_bytes(entry):
          file_b64 = UserChat.get_file_b64(entry)
          file_type = UserChat.get_file_type(entry)
          if _is_anthropic_supported_image(file_type):
            messages[-1]["content"].append({
              "type": "image",
              "source": {
                "type": "base64",
                "media_type": file_type,
                "data": file_b64
              }
            })
            Logger.info(f"Added history image to Anthropic: {file_type}")
          else:
            Logger.warning(f"Skipping unsupported history file for Anthropic: {file_type}")

        elif UserChat.is_file_uri(entry):
          file_uri = UserChat.get_file_uri(entry)
          file_type = UserChat.get_file_type(entry)
          if _is_anthropic_supported_image(file_type):
            try:
              encoded_data = await read_gcs_file_as_base64(file_uri)
              messages[-1]["content"].append({
                "type": "image",
                "source": {
                  "type": "base64",
                  "media_type": file_type,
                  "data": encoded_data
                }
              })
              Logger.info(f"Added GCS history image to Anthropic: {file_uri}")
            except Exception as e:
              Logger.error(f"Failed to read GCS file from history {file_uri}: {e}")
              # Continue processing without failing the entire conversion
              Logger.warning(f"Skipping GCS file due to read error: {file_uri}")
              raise
          else:
            Logger.warning(f"Skipping unsupported history file for Anthropic: {file_type}")
      else:
        Logger.warning("File entry found without corresponding user message in history")

  return messages


def _is_anthropic_supported_image(mime_type: str) -> bool:
  """
  Check if the mime type is supported by Anthropic's vision capabilities.
  
  Args:
    mime_type: The MIME type of the file
    
  Returns:
    bool: True if the file type is supported for vision
  """
  if not mime_type:
    return False

  supported_types = [
    "image/jpeg",
    "image/png", 
    "image/gif",
    "image/webp"
  ]
  return mime_type.lower() in supported_types


async def llm_generate_multimodal(prompt: str, llm_type: str,
                             user_file_bytes: bytes = None,
                             user_files: List[DataSourceFile] = None) -> str:
  """
  Generate text with an LLM given a file and a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use (default to gemini)
    user_file_bytes: bytes of the file provided by the user
    user_files: list of DataSourceFile objects for file meta data
  Returns:
    the text response: str
  """
  context = get_context()
  Logger.info(
    "LLM multimodal text generation initiated",
    extra={
      "operation": "llm_generate_multimodal",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "prompt_length": len(prompt) if prompt else 0,
      "prompt_preview": prompt[:50] + "..." if len(prompt) > 50\
          else prompt if prompt else "",
      "has_file_bytes": user_file_bytes is not None,
      "has_files": user_files is not None and len(user_files) > 0,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )
  # default to Gemini multimodal LLM
  if llm_type is None:
    llm_type = DEFAULT_MULTIMODAL_LLM_TYPE

  try:
    start_time = time.time()

    # for Google models, prioritize native client over langchain
    chat_llm_types = get_model_config().get_chat_llm_types()
    multimodal_llm_types = get_model_config().get_multimodal_llm_types()
    if llm_type in get_provider_models(PROVIDER_VERTEX):
      google_llm = get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      if google_llm is None:
        raise RuntimeError(
            f"Vertex model name not found for llm type {llm_type}")
      is_chat = llm_type in chat_llm_types
      is_multimodal = llm_type in multimodal_llm_types
      if not is_multimodal:
        raise RuntimeError(
            f"Vertex model {llm_type} needs to be multimodal")
      response = await google_llm_predict(prompt, is_chat, is_multimodal,
                            google_llm, None, None, user_file_bytes,
                            user_files)
    elif llm_type in get_provider_models(PROVIDER_ANTHROPIC):
      multimodal_llm_types = get_model_config().get_multimodal_llm_types()
      if llm_type not in multimodal_llm_types:
        raise RuntimeError(
            f"Anthropic model {llm_type} should be designated multimodal")
      response = await anthropic_predict(prompt, llm_type, stream=False,
                                       user_file_bytes=user_file_bytes,
                                       user_files=user_files)
    else:
      raise ResourceNotFoundException(f"Cannot find llm type '{llm_type}'")

    process_time = round(time.time() - start_time)
    Logger.info(
      "LLM generation latency",
      extra={
        "operation": "llm_generate_multimodal",
        "metric_type": "llm_generation_latency",
        "llm_type": llm_type,
        "duration_ms": round(process_time * 1000, 2),
        "request_id": context["request_id"],
        "trace": context["trace"],
        "session_id": context["session_id"]
      }
    )
    return response
  except Exception as e:
    raise InternalServerError(str(e)) from e

async def llm_chat(prompt: str, llm_type: str,
                   user_chat: Optional[UserChat] = None,
                   user_query: Optional[UserQuery] = None,
                   user_data: Optional[dict] = None,
                   chat_files: Optional[List[DataSourceFile]] = None,
                   chat_file_bytes: Optional[bytes] = None,
                   query_refs_str: Optional[str] = None,
                   stream: bool = False) -> \
                       Union[str, AsyncGenerator[str, None]]:
  """
  Send a prompt to a chat model and return string response or stream.
  Supports including a file in the chat context, either by URL or
  directly from file content.

  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use
    user_chat (optional): a user chat to use for context
    user_query (optional): a user query to use for context
    chat_files (optional) (List[DataSourceFile]): files to include in chat context
    chat_file_bytes (optional) (bytes): bytes of file to include in chat context
    query_refs_str: (optional): references for rag sources to include in prompt
    stream: whether to stream the response
  Returns:
    Either the full text response as str, or an AsyncGenerator
      yielding response chunks
  """
  context = get_context()
  Logger.info(
    "LLM chat generation initiated",
    extra={
      "operation": "llm_chat",
      "metric_type": "chat_generation",
      "llm_type": llm_type,
      "prompt_length": len(prompt) if prompt else 0,
      "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt if prompt else "",
      "chat_id": user_chat.id if user_chat else None,
      "query_id": user_query.id if user_query else None,
      "has_chat_file_bytes": chat_file_bytes is not None,
      "has_chat_files": chat_files is not None and len(chat_files) > 0,
      "with_file": chat_file_bytes is not None or (chat_files is not None and len(chat_files) > 0),
      "with_tools": False,  # Update if tools are used
      "stream": stream,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )

  if llm_type not in get_model_config().get_chat_llm_types():
    raise ResourceNotFoundException(f"Cannot find chat llm type '{llm_type}'")

  # validate chat file params and model for them
  is_multimodal = (llm_type in get_provider_models(PROVIDER_VERTEX) or
                   llm_type in get_provider_models(PROVIDER_ANTHROPIC))

  if chat_file_bytes is not None or chat_files:
    if chat_file_bytes is not None and chat_files:
      raise InternalServerError(
          "Must set only one of chat_file_bytes/chat_files")
    if not is_multimodal:
      raise InternalServerError("Chat files only supported for Vertex"
      " and Anthropic models")

  try:
    response = None

    # add chat history to prompt if necessary
    # Prompt history for gemini models is added using the native vertex API
    if ((user_chat is not None or user_query is not None)
         and "gemini" not in llm_type):
      context_prompt = get_context_prompt(
          user_chat=user_chat, user_query=user_query)
      # context_prompt includes only text (no images/video) from
      # user_chat.history and user_query.history
      prompt = context_prompt + "\n" + prompt

    # Add query references to the prompt if provided
    if query_refs_str:
      prompt += "\n\nReference information for retrieved information:"\
        + f" {query_refs_str}"

    # check whether the context length exceeds the limit for the model
    check_context_length(prompt, llm_type)

    # call the appropriate provider to generate the chat response
    if llm_type in get_provider_models(PROVIDER_LLM_SERVICE):
      is_chat = True
      response = await llm_service_predict(
          prompt, is_chat, llm_type, user_chat)
    elif llm_type in get_provider_models(PROVIDER_TRUSS):
      model_endpoint = get_provider_value(
          PROVIDER_TRUSS, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_truss_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_VLLM):
      model_endpoint = get_provider_value(
          PROVIDER_VLLM, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_vllm_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_MODEL_GARDEN):
      response = await model_garden_predict(prompt, llm_type)
    elif llm_type in get_provider_models(PROVIDER_ANTHROPIC):
      response = await anthropic_predict(prompt, llm_type, stream=stream,
                                  user_file_bytes=chat_file_bytes,
                                  user_files=chat_files,
                                  user_chat=user_chat)
    elif llm_type in get_provider_models(PROVIDER_VERTEX):
      google_llm = get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      if google_llm is None:
        raise RuntimeError(
            f"Vertex model name not found for llm type {llm_type}")
      is_chat = True
      system_prompt = get_model_system_prompt(llm_type)
      response = await google_llm_predict(prompt, is_chat, is_multimodal,
                                          google_llm, system_prompt, user_chat,
                                          chat_file_bytes, chat_files,
                                          user_data=user_data,
                                          stream=stream)
    elif llm_type in get_provider_models(PROVIDER_LANGCHAIN):
      response = await langchain_llm_generate(prompt, llm_type, user_chat)
    return response
  except Exception as e:
    import traceback
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

def get_context_prompt(user_chat=None,
                       user_query=None) -> str:
  """
  Get context prompt for chat based on previous chat or query history.

  Args:
    user_chat (optional): previous user chat
    user_query (optional): previous user query
  Returns:
    string context prompt
  """
  context_prompt = ""
  prompt_list = []
  if user_chat is not None:
    history = user_chat.history
    for entry in history:
      content = UserChat.entry_content(entry)
      if UserChat.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserChat.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
      # prompt_list includes only text from user_chat.history

  if user_query is not None:
    history = user_query.history
    for entry in history:
      content = UserQuery.entry_content(entry)
      if UserQuery.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserQuery.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
      # prompt_list includes only text from user_query.history

  context_prompt = "\n\n".join(prompt_list)

  return context_prompt

def check_context_length(prompt, llm_type):
  """
  Check whether a prompt exceeds the maximum context length for
  a model.

  Raise an exception if max context length exceeded.
  """
  # check if prompt exceeds context window length for model
  # assume a constant relationship between tokens and chars
  # TODO: Recalculate max_context_length for text prompt,
  # subtracting out tokens used by non-text context (image, video, etc)
  token_length = len(prompt) / CHARS_PER_TOKEN
  max_context_length = get_model_config_value(llm_type,
                                              KEY_MODEL_CONTEXT_LENGTH,
                                              None)
  if max_context_length and token_length > max_context_length:
    msg = f"Token length {token_length} exceeds llm_type {llm_type} " + \
          f"Max context length {max_context_length}"
    Logger.error(msg)
    raise ContextWindowExceededException(msg)

async def llm_truss_service_predict(llm_type: str, prompt: str,
                                    model_endpoint: str,
                                    parameters: dict = None) -> str:
  """
  Send a prompt to an instance of the LLM service and return response.
  Args:
    llm_type:
    prompt: the text prompt to pass to the LLM
    model_endpoint: model endpoint ip to be used for prediction and port number
      (e.g: xx.xxx.xxx.xx:8080)
    parameters (optional):  parameters to be used for prediction
  Returns:
    the text response: str
  """
  if parameters is None:
    parameters = get_provider_value(
        PROVIDER_TRUSS, KEY_MODEL_PARAMS, llm_type)

  parameters.update({"prompt": f"'{prompt}'"})

  api_url = f"http://{model_endpoint}/v1/models/model:predict"
  context = get_context()
  Logger.info(
    "Text generation using Truss Hosted Model initiated",
    extra={
      "operation": "llm_truss_service_predict",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "api_url": api_url,
      "prompt_length": len(prompt) if prompt else 0,
      "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt if prompt else "",
      "has_parameters": parameters is not None,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )

  resp = post_method(api_url, request_body=parameters)

  if resp.status_code != 200:
    raise InternalServerError(
      f"Error status {resp.status_code}: {str(resp)}")

  json_response = resp.json()

  Logger.info(
    "Truss service response received",
    extra={
      "operation": "llm_truss_service_predict",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "response_status": "success",
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )
  output = json_response["data"]["generated_text"]

  # if the prompt is repeated as part of the response, remove it
  output = output.replace(prompt, "").strip()
  # Llama 2 often adds quotes
  if output.startswith('"') or output.startswith("'"):
    output = output[1:]
  if output.endswith('"') or output.endswith("'"):
    output = output[:-1]

  return output

async def llm_vllm_service_predict(llm_type: str, prompt: str,
                                   model_endpoint: str,
                                   parameters: dict = None) -> str:
  """
  Send a prompt to an instance of the vllm service using the openai api.
  Assumes that the vllm server is only hosting a single model and will call the
  first model returned by client.models.list.
  Args:
    llm_type:
    prompt: the text prompt to pass to the LLM
    model_endpoint: model endpoint ip to be used for prediction and port number
      (e.g: xx.xxx.xxx.xx:8080)
    parameters (optional):  parameters to be used for prediction
  Returns:
    the text response: str
  """
  context = get_context()
  if parameters is None:
    parameters = get_provider_value(
        PROVIDER_VLLM, KEY_MODEL_PARAMS, llm_type)

  if parameters is None:
    parameter_kwargs = {}
  else:
    parameter_kwargs = dict(parameters)

  openai_api_key = "EMPTY"  # Not required for vLLM
  openai_api_base = f"http://{model_endpoint}/v1"

  client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
  )

  try:
    models = client.models.list()
    model = models.data[0].id

    Logger.info(
      "Text generation with vLLM hosted model initiated",
      extra={
        "operation": "llm_vllm_service_predict",
        "metric_type": "llm_generation",
        "llm_type": llm_type,
        "model": model,
        "api_base": openai_api_base,
        "prompt_length": len(prompt) if prompt else 0,
        "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt if prompt else "",
        "has_parameters": parameters is not None,
        "request_id": context["request_id"],
        "trace": context["trace"],
        "session_id": context["session_id"]
      }
    )

    response = client.chat.completions.create(
        model=model,
        messages=[
          {"role": "user", "content": prompt}
        ],
        **parameter_kwargs
    )
    output = response.choices[0].message.content
    Logger.info(
      "Response from vLLM service received",
      extra={
        "operation": "llm_vllm_service_predict",
        "metric_type": "llm_generation",
        "llm_type": llm_type,
        "response_status": "success",
        "request_id": context["request_id"],
        "trace": context["trace"],
        "session_id": context["session_id"]
      }
    )

  except OpenAIError as e:
    Logger.error(f"OpenAI API error: {e}")
    raise InternalServerError(f"Error: {e}") from e

  return output

async def llm_service_predict(prompt: str, is_chat: bool,
                              llm_type: str, user_chat=None,
                              auth_token: str = None) -> str:
  """
  Send a prompt to an instance of the LLM service and return response.

  Args:
    prompt: the text prompt to pass to the LLM
    is_chat: true if the model is a chat model
    llm_type: the type of LLM to use
    user_chat (optional): a user chat to use for context
    auth_token:

  Returns:
    the text response: str
  """
  context = get_context()
  llm_service_config = get_model_config().get_provider_config(
      PROVIDER_LLM_SERVICE)
  if not auth_token:
    auth_client = UserCredentials(llm_service_config.get("user"),
                                  llm_service_config.get("password"))
    auth_token = auth_client.get_id_token()

  # start with base url of the LLM service we are calling
  api_url = llm_service_config.get(KEY_MODEL_ENDPOINT)

  if is_chat:
    if user_chat:
      path = "/chat/{user_chat.id}"
    else:
      path = "/chat"
  else:
    path = "/llm/generate"
  api_url = api_url + path

  request_body = {
    "prompt": prompt,
    "llm_type": llm_type
  }

  Logger.info(
    "LLM service request initiated",
    extra={
      "operation": "llm_service_predict",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "api_url": api_url,
      "is_chat": is_chat,
      "has_user_chat": user_chat is not None,
      "chat_id": user_chat.id if user_chat else None,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )
  resp = post_method(api_url,
                     request_body=request_body,
                     token=auth_token)

  if resp.status_code != 200:
    raise InternalServerError(
      f"Error status {resp.status_code}: {str(resp)}")

  json_response = resp.json()

  Logger.info(
    "LLM service response received",
    extra={
      "operation": "llm_service_predict",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "response_status": "success",
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )
  output = json_response["content"]
  return output

async def model_garden_predict(prompt: str,
                               llm_type: str,
                               parameters: dict = None) -> str:
  """
  Generate text with a Model Garden model.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type:
    parameters (optional):  parameters to be used for prediction
  Returns:
    the prediction text.
  """
  context = get_context()
  aip_endpoint_name = get_provider_value(
      PROVIDER_MODEL_GARDEN, KEY_MODEL_ENDPOINT, llm_type)

  sub_provider_name = get_provider_value(
      PROVIDER_MODEL_GARDEN, KEY_SUB_PROVIDER, llm_type)

  if str(sub_provider_name) == str(SUB_PROVIDER_OPENAPI):
    creds, _ = google.auth.default()
    if not creds.valid:
      auth_req = google.auth.transport.requests.Request()
      creds.refresh(auth_req)
    auth_token = creds.token

    openapi_endpoint = f"https://{REGION}-aiplatform.googleapis.com/" \
                       f"v1/projects/{PROJECT_ID}/locations/{REGION}/" \
                      f"endpoints/openapi/chat/completions"
    req_headers = {"Authorization": f"Bearer {auth_token}",
                   "Content-Type": "application/json"}
    req_body = {"model": f"{aip_endpoint_name}",
                "messages":[{"role": "user",
                             "content": f"{prompt}"}]}
    Logger.info(
      "Text generation using OpenAPI for Model Garden initiated",
      extra={
        "operation": "model_garden_predict",
        "metric_type": "llm_generation",
        "llm_type": llm_type,
        "endpoint": openapi_endpoint,
        "prompt_length": len(prompt) if prompt else 0,
        "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt if prompt else "",
        "request_id": context["request_id"],
        "trace": context["trace"],
        "session_id": context["session_id"]
      }
    )

    resp = requests.post(
      url=f"{openapi_endpoint}", json=req_body, headers=req_headers,
      timeout=DEFAULT_TIMEOUT)

    if resp.status_code != 200:
      raise InternalServerError(
        f"Error status {resp.status_code}: {str(resp)}")

    json_response = resp.json()
    Logger.info(
      "Model Garden OpenAPI response received",
      extra={
        "operation": "model_garden_predict",
        "metric_type": "llm_generation",
        "llm_type": llm_type,
        "response_status": "success",
        "request_id": context["request_id"],
        "trace": context["trace"],
        "session_id": context["session_id"]
      }
    )
    output = json_response["choices"][0]["message"]["content"]
    return output

  aip_endpoint = f"projects/{PROJECT_ID}/locations/" \
                 f"{REGION}/endpoints/{aip_endpoint_name}"
  Logger.info(
    "Text generation with Model Garden initiated",
    extra={
      "operation": "model_garden_predict",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "endpoint": aip_endpoint,
      "prompt_length": len(prompt) if prompt else 0,
      "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt if prompt else "",
      "has_parameters": parameters is not None,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )

  if parameters is None:
    parameters = get_provider_value(PROVIDER_MODEL_GARDEN,
                                    KEY_MODEL_PARAMS, llm_type)

  parameters.update({"prompt": f"'{prompt}'"})

  instances = [parameters, ]
  endpoint_without_peft = google.cloud.aiplatform.Endpoint(aip_endpoint)

  response = await endpoint_without_peft.predict_async(instances=instances)

  predictions_text = "\n".join(response.predictions)
  Logger.info(
    "Model Garden response received",
    extra={
      "operation": "model_garden_predict",
      "metric_type": "llm_generation",
      "llm_type": llm_type,
      "model_resource_name": response.model_resource_name,
      "model_version_id": response.model_version_id,
      "predictions_count": len(response.predictions),
      "response_status": "success",
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )

  return predictions_text

def convert_history_to_gemini_prompt(history: list, is_multimodal:bool=False
                                     ) -> list[Content]:
  """converts a user chat history inot a properly formatted gemini prompt
  history: A history entry from a UserChat object
  is_multimodal: If the model is multimodal
  Returns a properly formatted gemini prompt to be used for generating a 
  response"""
  conversation: list[Content] = []
  for entry in history:
    content = UserChat.entry_content(entry)
    if UserChat.is_human(entry):
      conversation.append(Content(role="user", parts=[Part.from_text(content)]))
    elif UserChat.is_ai(entry):
      conversation.append(Content(role="model", parts=[Part.from_text(content)]))
    elif UserChat.is_full_query_response(entry):
      conversation.append(
        Content(role="model", parts=[Part.from_text(
          UserChat.convert_query_response_to_chat_entry(entry))]))
    elif is_multimodal and conversation:
      # TODO: Currently Genie doesn't track if the user or model added a file,
      # it's assumed that the role is the same as for the previous entry
      # therefore we skip adding the file to history if it's the first entry,
      # which shouldn't currently be possible in genie anyways
      role = conversation[-1].role
      part = None
      if UserChat.is_file_bytes(entry):
        part = Part.from_data(base64.b64decode(UserChat.get_file_b64(entry)),
                          mime_type=UserChat.get_file_type(entry))
      elif UserChat.is_file_uri(entry):
        part = Part.from_uri(UserChat.get_file_uri(entry),
                                    mime_type=UserChat.get_file_type(entry))
      if part:
        conversation.append(Content(role=role, parts=[part]))
  return conversation

async def google_llm_predict(prompt: str, is_chat: bool, is_multimodal: bool,
                google_llm: str, system_prompt: str=None,
                user_chat: Optional[UserChat]=None,
                user_file_bytes: bytes=None,
                user_files: List[DataSourceFile]=None,
                user_data: Optional[dict]=None,
                stream: bool=False) -> Union[str, AsyncGenerator[str, None]]:
  """
  Generate text with a Google multimodal LLM given a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    is_chat: true if the model is a chat model
    is_multimodal: true if the model is a multimodal model
    google_llm: name of the vertex llm model
    system_prompt: system prompt to use for chat models
    user_chat: chat history
    user_file_bytes: the bytes of the file provided by the user
    user_files: list of DataSourceFiles for files provided by the user
    stream: whether to stream the response
  Returns:
    Either the full text response as str, or an AsyncGenerator yielding response chunks
  """
  context = get_context()
  Logger.info(
    "Text generation with Google multimodal LLM initiated",
    extra={
      "operation": "google_llm_predict",
      "metric_type": "llm_generation",
      "llm_type": google_llm,
      "prompt_length": len(prompt) if prompt else 0,
      "prompt_preview": prompt[:50] + "..." if len(prompt) > 50 else prompt if prompt else "",
      "is_chat": is_chat,
      "is_multimodal": is_multimodal,
      "has_user_file_bytes": user_file_bytes is not None,
      "has_user_files": user_files is not None and len(user_files) > 0,
      "with_file": user_file_bytes is not None or (user_files is not None and len(user_files) > 0),
      "chat_id": user_chat.id if user_chat else None,
      "stream": stream,
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )

  # TODO: Remove this section after non-gemini llms are removed from
  # the model options
  _ = user_data #used in metrics tracking
  prompt_list = []
  if user_chat is not None:
    history = user_chat.history
    for entry in history:
      content = UserChat.entry_content(entry)
      if UserChat.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserChat.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
      elif is_multimodal:
        if UserChat.is_file_bytes(entry):
          prompt_list.append(
            Part.from_data(base64.b64decode(UserChat.get_file_b64(entry)),
                            mime_type=UserChat.get_file_type(entry)))
        elif UserChat.is_file_uri(entry):
          prompt_list.append(Part.from_uri(UserChat.get_file_uri(entry),
                                      mime_type=UserChat.get_file_type(entry)))
  prompt_list.append(prompt)
  # the context prompt is only used for non-gemini models and cannot handle
  # the gemini Part object
  context_prompt = "\n\n".join(entry for entry in prompt_list
                               if isinstance(entry, str))

  # Get model params at the model level else use global vertex params.
  parameters = get_provider_value(PROVIDER_VERTEX, KEY_MODEL_PARAMS)
  provider_config = get_provider_model_config(PROVIDER_VERTEX)
  for _, model_config in provider_config.items():
    model_name = model_config.get(KEY_MODEL_NAME)
    if model_name == google_llm and KEY_MODEL_PARAMS in model_config:
      parameters = model_config.get(KEY_MODEL_PARAMS)

  try:
    if is_chat:
      # gemini uses new "GenerativeModel" class and requires different params
      if "gemini" in google_llm:
        prompt_list = []
        if user_chat:
          prompt_list.extend(
            convert_history_to_gemini_prompt(user_chat.history, is_multimodal))
        prompt_list.append(Content(role="user", parts=[Part.from_text(prompt)]))
        chat_model = GenerativeModel(google_llm, system_instruction=system_prompt)
        if is_multimodal:
          if user_file_bytes is not None and user_files is not None:
            # user_file_bytes refers to a single image and so we index into
            # user_files (a list) to get a single mime type
            prompt_list.append(Content( role="user", parts=[
              Part.from_data(user_file_bytes,
                             mime_type=user_files[0].mime_type)]))
          elif user_files is not None:
            # user_files is a list referring to one or more images
            for user_file in user_files:
              prompt_list.append(Content(role="user", parts=[
                Part.from_uri(user_file.gcs_path,
                              mime_type=user_file.mime_type)]))
        # Logger.info(f"context list {prompt_list}")
        for l in prompt_list:
          Logger.debug(l if len(str(l)) < 50 else str(l)[:49])
        generation_config = GenerationConfig(**parameters)
        response = await chat_model.generate_content_async(prompt_list,
            generation_config=generation_config,
            safety_settings=SAFETY_SETTINGS,
            stream=stream)

        if stream:
          async def response_generator():
            try:
              async for chunk in response:
                if chunk.text:
                  yield chunk.text
            except ValueError as e:
              if "Cannot get the Candidate text." in str(e):
                candidate_info = ""
                candidate_start = str(e).find("Candidate:")
                if candidate_start != -1:
                  candidate_info = str(e)[candidate_start:]
                yield (
                  " \n ...I'm sorry, any further response has been blocked because the "
                  "succeeding content violates my safety filters.\n"
                  f"Details: {candidate_info}"
                )
                return
              else:
                raise
            except Exception as e:
              raise InternalServerError(str(e)) from e
          return response_generator()

        return response.text

      else:
        chat_model = ChatModel.from_pretrained(google_llm)
        chat = chat_model.start_chat()
        response = await chat.send_message_async(context_prompt, **parameters)
    else:
      text_model = TextGenerationModel.from_pretrained(google_llm)
      response = await text_model.predict_async(
          context_prompt,
          **parameters,
      )

  except Exception as e:
    raise InternalServerError(str(e)) from e

  Logger.info(
    "Google LLM response received",
    extra={
      "operation": "google_llm_predict",
      "metric_type": "llm_generation",
      "llm_type": google_llm,
      "response_length": len(response.text) if hasattr(response, "text") else 0,
      "response_status": "success",
      "request_id": context["request_id"],
      "trace": context["trace"],
      "session_id": context["session_id"]
    }
  )
  response = response.text

  return response

async def generate_chat_summary(user_chat: UserChat) -> str:
  """
  Generate a summary/title for a chat using the default summary model.

  Args:
    user_chat: UserChat object containing the chat history to summarize

  Returns:
    str: Generated summary text, cleaned and truncated to max 100 chars
  """
  # Build prompt from chat history
  history_text = []
  for entry in user_chat.history:
    if UserChat.is_human(entry):
      history_text.append(f"Human: {UserChat.entry_content(entry)}")
    elif UserChat.is_ai(entry):
      history_text.append(f"Assistant: {UserChat.entry_content(entry)}")

  chat_text = "\n".join(history_text)

  summary_prompt = (
    "Please generate a brief, informative title (maximum 100 characters) "
    "that captures the main topic or purpose of this conversation. "
    "Respond with only the title text.\n\n"
    f"Conversation:\n{chat_text}"
  )

  # Generate summary using the default summary model
  summary = await llm_chat(
    prompt=summary_prompt,
    llm_type=DEFAULT_CHAT_SUMMARY_MODEL
  )

  # Clean up summary - remove quotes and limit length
  summary = summary.strip('" \n').strip("' \n")
  if len(summary) > 100:
    summary = summary[:97] + "..."

  return summary

def get_models_for_user(user_data: dict, is_multimodal: Optional[bool] = None
                        ) -> list[str]:
  """Takes the user's informaiton and whether they want multimodal models
  then returns a list of model names the user has access to """
  model_config = get_model_config()
  if is_multimodal is True:
    llm_types = model_config.get_multimodal_chat_llm_types()
  elif is_multimodal is False:
    llm_types = model_config.get_text_chat_llm_types()
  else: # multimodal is None
    llm_types = model_config.get_chat_llm_types()

  return [llm for llm in llm_types if
          model_config.is_model_enabled_for_user(llm, user_data)]
