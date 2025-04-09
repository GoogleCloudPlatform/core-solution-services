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

""" Chat endpoints """
import traceback
import json
import base64
import io
from typing import Optional
from fastapi import APIRouter, Depends, Form, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from common.models import User, UserChat, QueryEngine, QueryReference
from common.models.llm import (CHAT_FILE, CHAT_FILE_URL, CHAT_FILE_BASE64,
                               CHAT_FILE_TYPE)
from common.utils.auth_service import validate_token
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError,
                                 UnauthorizedUserError)
from common.utils.http_exceptions import (InternalServerError, BadRequest,
                                          ResourceNotFound)
from common.utils.logging_handler import Logger
from config import ERROR_RESPONSES, DEFAULT_CHAT_LLM_TYPE, get_model_config
from schemas.llm_schema import (ChatUpdateModel,
                                LLMGenerateModel,
                                LLMUserChatResponse,
                                LLMUserAllChatsResponse,
                                LLMGetTypesResponse,
                                LLMGetDetailsResponse)
from services.llm_generate import (llm_chat, generate_chat_summary,
                                   get_models_for_user)
from services.agents.agent_tools import chat_tools, run_chat_tools
from services.query.query_service import query_generate_for_chat
from utils.file_helper import process_chat_file, validate_multimodal_file_type

Logger = Logger.get_logger(__file__)
router = APIRouter(prefix="/chat", tags=["Chat"], responses=ERROR_RESPONSES)

@router.get(
    "/chat_types",
    name="Get all Chat LLM types",
    response_model=LLMGetTypesResponse)
def get_chat_llm_list(user_data: dict = Depends(validate_token),
                    is_multimodal: Optional[bool] = None):
  """
  Get available Chat LLMs, optionally filter by
  multimodal capabilities. Returns basic model information.

  Args:
    is_multimodal: `bool`
      Optional: If True, only multimodal LLM types are returned.
        If False, only non-multimodal LLM types are returned.
        If None, all LLM types are returned.

  Returns:
      LLMGetTypesResponse with basic model information
  """
  Logger.info("Entering chat/chat_types")
  try:
    user_enabled_llms = get_models_for_user(user_data, is_multimodal)
    return {
      "success": True,
      "message": "Successfully retrieved chat llm types",
      "data": user_enabled_llms
    }
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

@router.get(
    "/chat_types/details",
    name="Get detailed Chat LLM information",
    response_model=LLMGetDetailsResponse)
def get_chat_llm_details(user_data: dict = Depends(validate_token),
                      is_multimodal: Optional[bool] = None):
  """
  Get available Chat LLMs with detailed information, optionally filter by
  multimodal capabilities

  Args:
    is_multimodal: `bool`
      Optional: If True, only multimodal LLM types are returned.
        If False, only non-multimodal LLM types are returned.
        If None, all LLM types are returned.

  Returns:
      LLMGetDetailsResponse with detailed model information
  """
  Logger.info("Entering chat/chat_types/details")
  try:
    model_config = get_model_config()
    llm_types = get_models_for_user(user_data, is_multimodal)
    model_details = []
    for llm in llm_types:
      config = model_config.get_model_config(llm)

      # Get model parameters from config
      model_params = config.get("model_params", {})

      # Get provider parameters and merge with model params
      _, provider_config = model_config.get_model_provider_config(llm)
      if provider_config and "model_params" in provider_config:
        # Provider params are the base, model params override them
        merged_params = provider_config["model_params"].copy()
        merged_params.update(model_params)
        model_params = merged_params

      model_details.append({
        "id": llm,
        "name": config.get("name", ""),
        "description": config.get("description", ""),
        "capabilities": config.get("capabilities", []),
        "date_added": config.get("date_added", ""),
        "is_multi": config.get("is_multi", False),
        "model_params": model_params
      })

    Logger.info(f"Chat LLM models for user {model_details}")
    return {
      "success": True,
      "message": "Successfully retrieved chat llm details",
      "data": model_details
    }
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

@router.get(
    "",
    name="Get all user chats",
    response_model=LLMUserAllChatsResponse)
def get_chat_list(skip: int = 0, limit: int = 20,
                with_all_history: bool = False,
                with_first_history: bool = False,
                user_data: dict = Depends(validate_token)):
  """
  Get user chats for authenticated user.  Chat data does not include
  chat history to slim payload.  To retrieve chat history use the
  get single chat endpoint.

  Args:
    skip: `int`
      Number of tools to be skipped <br/>
    limit: `int`
      Size of tools array to be returned <br/>

  Returns:
      LLMUserAllChatsResponse
  """
  try:
    if skip < 0:
      raise ValidationError("Invalid value passed to \"skip\" query parameter")

    if limit < 1:
      raise ValidationError("Invalid value passed to \"limit\" query parameter")

    user = User.find_by_email(user_data.get("email"))
    user_chats = UserChat.find_by_user(user.user_id)

    chat_list = []
    for i in user_chats:
      chat_data = i.get_fields(reformat_datetime=True)
      chat_data["id"] = i.id
      # Trim chat history to slim return payload
      if not with_all_history and not with_first_history:
        del chat_data["history"]
      elif with_first_history:
        # Trim all chat history except the first one
        chat_data["history"] = chat_data["history"][:1]
      chat_list.append(chat_data)
    return {
      "success": True,
      "message": f"Successfully retrieved user chats for user {user.user_id}",
      "data": chat_list
    }
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.get(
    "/{chat_id}",
    name="Get user chat",
    response_model=LLMUserChatResponse)
def get_chat(chat_id: str,
             user_data: dict = Depends(validate_token)):
  """
  Get a specific user chat by id

  Returns:
      LLMUserChatResponse
  """
  try:
    user_chat = UserChat.find_by_id(chat_id)
    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id
    user = User.find_by_email(user_data.get("email"))
    if user.user_id != user_chat.user_id:
      raise UnauthorizedUserError("User is not allowed to access this chat.")

    return {
      "success": True,
      "message": f"Successfully retrieved user chat {chat_id}",
      "data": chat_data
    }
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.put(
  "/{chat_id}",
  name="Update user chat"
)
def update_chat(chat_id: str,
                input_chat: ChatUpdateModel,
                user_data: dict = Depends(validate_token)):
  """Update a user chat

  Args:
    input_chat (ChatUpdateModel): fields in body of chat to update.
      Fields that can be updated are the title and history.

  Raises:
    ResourceNotFoundException: If the Chat does not exist
    HTTPException: 500 Internal Server Error if something fails
    UnauthorizedUserError: If user did not create this chat

  Returns:
    [JSON]: {'success': 'True'} if the chat is updated,
    NotFoundErrorResponseModel if the chat not found,
    InternalServerErrorResponseModel if the chat update raises an exception
  """
  try:
    input_chat_dict = {**input_chat.dict()}

    existing_chat = UserChat.find_by_id(chat_id)
    user = User.find_by_email(user_data.get("email"))
    if user.user_id != existing_chat.user_id:
      raise UnauthorizedUserError("User is not allowed to update this chat.")

    for key in input_chat_dict:
      if input_chat_dict.get(key) is not None:
        setattr(existing_chat, key, input_chat_dict.get(key))
    # if the chat was created as empty we add the intial user prompt if
    # available
    if not existing_chat.prompt and len(existing_chat.history) > 1:
      existing_chat.prompt = UserChat.entry_content(existing_chat.history[1])
    existing_chat.update()

    return {
      "success": True,
      "message": f"Successfully updated user chat {chat_id}",
      "data": existing_chat.get_fields(reformat_datetime=True)
    }
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e


@router.delete(
  "/{chat_id}",
  name="Delete user chat"
)
def delete_chat(chat_id: str, hard_delete=False):
  """Delete a user chat. We default to soft delete.

  Args:
    chat_id: id of user chat to delete.
    hard_delete: if True delete the chat model permanantly.

  Raises:
    ResourceNotFoundException: If the Chat does not exist
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [JSON]: {'success': 'True'} if the chat is deleted,
    NotFoundErrorResponseModel if the chat not found,
    InternalServerErrorResponseModel if the chat deletion raises an exception
  """
  try:
    if hard_delete:
      UserChat.delete_by_id(chat_id)
      msg = f"Permanantly deleted user chat {chat_id}"
    else:
      UserChat.soft_delete_by_id(chat_id)
      msg = f"Successfully deleted user chat {chat_id}"
    return {
      "success": True,
      "message": msg,
    }
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e

def validate_tool_names(tool_names: Optional[str]):
  """Attempts to validate a tool_names input for chat, raises an error
  if the provided value is invalid"""
  if tool_names:
  # ensuring the tool names provided were properly formatted
    try:
      tool_names = json.loads(tool_names)
    except json.decoder.JSONDecodeError as e:
      raise HTTPException(
          status_code=422,
          detail=("Tool names must be a string representing a "
                 "json formatted list")) from e
    # ensuring the tools provided are valid for chat
    if invalid_tools := [tool for tool in tool_names if tool not in chat_tools]:
      failure_message = f"Invalid tool names: {','.join(invalid_tools)}"
      raise HTTPException(status_code=422, detail=failure_message)


@router.post(
    "",
    name="Create new chat",
    response_model=LLMUserChatResponse, deprecated=True)
async def create_chat(prompt: str = Form(None),
                     llm_type: str = Form(None),
                     stream: bool = Form(False),
                     history: str = Form(None),
                     chat_file: UploadFile = None,
                     chat_file_url: str = Form(None),
                     tool_names: str = Form(None),
                     query_engine_id: str = Form(None),
                     query_filter: str = Form(None),
                     user_data: dict = Depends(validate_token)):
  """Create new chat for authenticated user

  Args:
      prompt: the text prompt to pass to the LLM
      llm_type: the type of LLM to use
      stream: whether to stream the response
      history: optional JSON string containing chat history
      chat_file: optional file to include in chat context
      chat_file_url: optional URL to file to include in chat context
      tool_names: optional JSON string containing list of tool names
      query_engine_id: optional ID of the query engine to use
      query_filter: optional JSON string containing query filter
      user_data: dict containing user information from auth token

  Returns:
      LLMUserChatResponse
  """
  try:
    # Validate required parameters first
    if not prompt and not history:
      raise ValidationError("Either prompt or history must be provided")

    # Validate tool names if provided
    if tool_names:
      try:
        tool_names = json.loads(tool_names)
      except json.decoder.JSONDecodeError as exc:
        raise HTTPException(
          status_code=422,
          detail=("Tool names must be a string representing a "
                 "json formatted list")) from exc
      # ensuring the tools provided are valid for chat
      if invalid_tools := \
          [tool for tool in tool_names if tool not in chat_tools]:
        raise HTTPException(
          status_code=422,
          detail=f"Invalid tool names: {','.join(invalid_tools)}"
        )

    user = User.find_by_email(user_data.get("email"))

    # New: Handle query engine if specified
    query_engine = None
    if query_engine_id:
      query_engine = QueryEngine.find_by_id(query_engine_id)
      if not query_engine:
        raise ResourceNotFoundException(
            f"Query engine {query_engine_id} not found")

    # Process chat file(s): upload to GCS and determine mime type
    chat_file_bytes = None
    chat_files = None
    if chat_file is not None or chat_file_url is not None:
      chat_files = await process_chat_file(chat_file, chat_file_url)

    # Only read chat file bytes if we can't upload the file(s) to GCS
    if not chat_files and chat_file is not None:
      await chat_file.seek(0)
      chat_file_bytes = await chat_file.read()

    # If history is provided, parse the JSON string into a list
    if history:
      try:
        history_list = json.loads(history)  # Parse the JSON string into a list
        if not isinstance(history_list, list):
          raise ValidationError("History must be a JSON array")
      except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in history: {str(e)}") from e

      user_chat = UserChat(user_id=user.user_id, llm_type=llm_type,
                         prompt=prompt)
      user_chat.history = history_list  # Use the parsed list
      if chat_file:
        user_chat.update_history(custom_entry={
          f"{CHAT_FILE}": chat_file.filename
        })
      elif chat_file_url:
        user_chat.update_history(custom_entry={
          f"{CHAT_FILE_URL}": chat_file_url
        })
      user_chat.save()

      # Generate and set chat title
      summary = await generate_chat_summary(user_chat)
      user_chat.title = summary
      user_chat.save()

      chat_data = user_chat.get_fields(reformat_datetime=True)
      chat_data["id"] = user_chat.id

      return {
          "success": True,
          "message": "Successfully created chat from history",
          "data": chat_data
      }

    # Handle prompt-based chat creation
    response_files = None
    query_result = None
    query_references = None
    context_files = chat_files or []  # Initialize with any uploaded files

    if tool_names:
      response, response_files = run_chat_tools(prompt)
    else:
      if query_engine:
        # Generate query response if query engine specified
        query_references, query_content_files = await query_generate_for_chat(
          user.id,
          prompt,
          query_engine,
          user_data,
          rank_sentences=False,
          query_filter=json.loads(query_filter) if query_filter else None
        )

        # Add query content files to context files
        if query_content_files:
          context_files.extend(query_content_files)

        # Add reference text to prompt
        query_refs_str = QueryReference.reference_list_str(query_references)
        prompt += "\n\n" + \
          f"A search of the {query_engine.name} Source produced " \
          f"these references: {query_refs_str}"

      # Normal chat response with combined context files
      response = await llm_chat(prompt,
                            llm_type,
                            chat_files=context_files,
                            chat_file_bytes=chat_file_bytes,
                            stream=stream)

      if stream:
        # Return streaming response
        return StreamingResponse(
            response,
            media_type="text/event-stream"
        )

    # Create new chat for user
    user_chat = UserChat(user_id=user.user_id, llm_type=llm_type,
                       prompt=prompt)

    # Update history with all components
    user_chat.history = UserChat.get_history_entry(prompt, response)

    if chat_file:
      user_chat.update_history(custom_entry={
        f"{CHAT_FILE}": chat_file.filename
      })
    elif chat_file_url:
      user_chat.update_history(custom_entry={
        f"{CHAT_FILE_URL}": chat_file_url
      })

    if response_files:
      for file in response_files:
        user_chat.update_history(custom_entry={
          CHAT_FILE: file["name"]
        })
        user_chat.update_history(custom_entry={
          CHAT_FILE_BASE64: file["contents"]
        })

    # New: Add query engine results to history
    if query_engine:
      user_chat.update_history(
        query_engine=query_engine,
        query_result=query_result,
        query_references=query_references
      )

    user_chat.save()

    # Generate and set chat title
    summary = await generate_chat_summary(user_chat)
    user_chat.title = summary
    user_chat.save()

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    return {
        "success": True,
        "message": "Successfully created chat",
        "data": chat_data
    }

  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except HTTPException:
    raise  # Let FastAPI HTTPExceptions pass through
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post("/empty_chat", name="Create new chat")
async def create_empty_chat(user_data: dict = Depends(validate_token)):
  """
  Create new chat for authenticated user.
  Returns:
      Data for the newly created chat
  """
  Logger.info(f"Creating new chat for {user_data}")

  try:
    user = User.find_by_email(user_data.get("email"))
    # create new chat for user
    user_chat = UserChat(user_id=user.user_id)
    user_chat.save()
    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id
    return {
        "success": True,
        "message": "Successfully created chat",
        "data": chat_data
    }
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/{chat_id}/generate")
async def user_chat_generate(chat_id: str, gen_config: LLMGenerateModel):
  """
  Continue chat based on context of user chat

  Args:
    chat_id: ID of the chat to continue
    gen_config: llm generation parameters

  Returns:
    LLMUserChatResponse or StreamingResponse
  """
  Logger.info(f"generating chat response for {chat_id}")
  tool_names = gen_config.tool_names
  validate_tool_names(tool_names)
  query_engine_id = gen_config.query_engine_id
  query_filter = gen_config.query_filter

  response_files = None

  try:
    # process chat file(s): upload to GCS and determine mime type
    chat_file_bytes = None
    chat_files = None
    chat_file = None
    if gen_config.chat_file_b64 and gen_config.chat_file_b64_name:
      content = base64.b64decode(gen_config.chat_file_b64)
      chat_file = UploadFile(io.BytesIO(content),
                            filename=gen_config.chat_file_b64_name,
                            size=len(content))
    chat_file_url = gen_config.chat_file_url
    if chat_file is not None or chat_file_url is not None:
      chat_files = await process_chat_file(chat_file, chat_file_url)

    genconfig_dict = {**gen_config.model_dump()}
    Logger.info(f"Generating new chat response for chat_id={chat_id},"
                f"genconfig_dict={genconfig_dict}")

    prompt = genconfig_dict.get("prompt")
    if prompt is None or prompt == "":
      return BadRequest("Missing or invalid payload parameters")

    # fetch user chat
    user_chat = UserChat.find_by_id(chat_id)
    if user_chat is None:
      raise ResourceNotFoundException(f"Chat {chat_id} not found ")

    # Check if chat needs a title
    if not user_chat.title or user_chat.title.strip() == "":
      # Generate and set chat title
      summary = await generate_chat_summary(user_chat)
      user_chat.title = summary
      user_chat.save()

    if (chat_file_bytes
        and (mime_type := validate_multimodal_file_type(chat_file.filename))):
      user_chat.update_history(custom_entry={
        CHAT_FILE_BASE64: chat_file_bytes,
        CHAT_FILE_TYPE: mime_type
      })
    if chat_files:
      for cur_chat_file in chat_files:
        user_chat.update_history(custom_entry={
          CHAT_FILE_URL: cur_chat_file.gcs_path,
          CHAT_FILE_TYPE: cur_chat_file.mime_type
        })

    # set llm type for chat
    llm_type = genconfig_dict.get("llm_type", None)
    if llm_type is None:
      llm_type = user_chat.llm_type or DEFAULT_CHAT_LLM_TYPE

    # get streaming mode
    stream = genconfig_dict.get("stream", False)

    try:
      query_result = None
      query_references = None
      context_files = chat_files or []  # Initialize with any uploaded files

      if tool_names:
        response, response_files = run_chat_tools(prompt)
      else:
        if query_engine_id:
          query_engine = QueryEngine.find_by_id(query_engine_id)
          if not query_engine:
            raise ResourceNotFoundException(
              f"Query engine {query_engine_id} not found")

          query_references, query_content_files = await query_generate_for_chat(
            user_chat.user_id,
            prompt,
            query_engine,
            None,  # No user data needed
            rank_sentences=False,
            query_filter=query_filter
          )

          # Add query content files to context files
          if query_content_files:
            context_files.extend(query_content_files)

          # Add reference text to prompt
          query_refs_str = QueryReference.reference_list_str(query_references)
          prompt += "\n\n" + \
              f"A search of the {query_engine.name} Source produced " \
              f"these references: {query_refs_str}"
        response = await llm_chat(prompt,
                              llm_type,
                              user_chat=user_chat,
                              chat_files=context_files,
                              chat_file_bytes=chat_file_bytes,
                              stream=stream)

        if stream:
          # Return streaming response
          return StreamingResponse(
            response,
            media_type="text/event-stream"
          )

      # save chat history
      user_chat.update_history(prompt=prompt, response=response)

      # New: Add query results to history if present
      if query_engine_id:
        user_chat.update_history(
          query_engine=query_engine,
          query_result=query_result,
          query_references=query_references
        )

      if response_files:
        for file in response_files:
          user_chat.update_history(custom_entry={
            CHAT_FILE: file["name"]
          })
          user_chat.update_history(custom_entry={
            CHAT_FILE_BASE64: file["contents"]
          })

      chat_data = user_chat.get_fields(reformat_datetime=True)
      chat_data["id"] = user_chat.id

      # save chat history
      user_chat.update_history(prompt=prompt, response=response)

      if response_files:
        for file in response_files:
          user_chat.update_history(custom_entry={
            CHAT_FILE: file["name"]
          })
          user_chat.update_history(custom_entry={
            CHAT_FILE_BASE64: file["contents"]
          })

      chat_data = user_chat.get_fields(reformat_datetime=True)
      chat_data["id"] = user_chat.id

      return {
        "success": True,
        "message": "Successfully generated text",
        "data": chat_data
      }
    except Exception as e:
      Logger.error(e)
      Logger.error(traceback.print_exc())
      raise InternalServerError(str(e)) from e

  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/{chat_id}/generate_summary",
    name="Generate chat summary and update title",
    response_model=LLMUserChatResponse)
async def generate_chat_summary_route(chat_id: str):
  """
  Generate a summary of the chat using the default summary model and 
  update the chat title with that summary.

  Args:
      chat_id: ID of the chat to summarize

  Returns:
      LLMUserChatResponse with the updated chat data
  """
  try:
    # Get the chat
    user_chat = UserChat.find_by_id(chat_id)
    if user_chat is None:
      raise ResourceNotFoundException(f"Chat {chat_id} not found")

    # Generate summary and update title
    summary = await generate_chat_summary(user_chat)
    user_chat.title = summary
    user_chat.save()

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    return {
      "success": True,
      "message": "Successfully generated summary and updated chat title",
      "data": chat_data
    }

  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e
