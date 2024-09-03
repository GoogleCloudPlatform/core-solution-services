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
import os
import traceback
from typing import Union, Annotated
from fastapi import APIRouter, Depends, Form, UploadFile
from common.models import User, UserChat
from common.utils.auth_service import validate_token
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError)
from common.utils.http_exceptions import (InternalServerError, BadRequest,
                                          ResourceNotFound)
from common.utils.logging_handler import Logger
from config import ERROR_RESPONSES, DEFAULT_CHAT_LLM_TYPE, get_model_config
from schemas.llm_schema import (ChatUpdateModel,
                                LLMChatModel,
                                LLMUserChatResponse,
                                LLMUserAllChatsResponse,
                                LLMGetTypesResponse)
from services.llm_generate import llm_chat
from utils.file_helper import process_upload_file, validate_multi_file_type

Logger = Logger.get_logger(__file__)
router = APIRouter(prefix="/chat", tags=["Chat"], responses=ERROR_RESPONSES)

async def process_chat_file(chat_file, chat_file_url, bucket=None):
  chat_file_type = None
  is_valid = False
  if chat_file is not None:
    if chat_file_url is not None:
      raise ValidationError("cannot set both upload_file and file_url")
    chat_file_url = await process_upload_file(chat_file, bucket)
    chat_file_type = validate_multi_file_type(chat_file.filename)
    if chat_file_type is None:
      raise ValidationError(
          f"unsupported file type upload file {chat_file.filename}")
  elif chat_file_url:
    if not (chat_file_url.startswith("gs://")
            or chat_file_url.startswith("http://")
            or chat_file_url.startswith("https://")
            or chat_file_url.startswith("shpt://")):
      return BadRequest(
          "chat_file_url must start with gs://, http:// or https://, shpt://")
    # check file type from extension if present
    chat_file_name = os.path.basename(chat_file_url)
    file_extension = os.path.splitext(chat_file_name)[1]
    if file_extension:
      chat_file_type = validate_multi_file_type(chat_file_name)
      if not is_valid:
        raise ValidationError(
            f"unsupported file type file url {chat_file_url}")
    else:
      # assume html if no extension
      chat_file_type = "text/html"
  return chat_file_url, chat_file_type

@router.get(
    "/chat_types",
    name="Get all Chat LLM types",
    response_model=LLMGetTypesResponse)
def get_chat_llm_list():
  """
  Get available Chat LLMs

  Returns:
      LLMGetTypesResponse
  """
  try:
    return {
      "success": True,
      "message": "Successfully retrieved chat llm types",
      "data": get_model_config().get_chat_llm_types()
    }
  except Exception as e:
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
def get_chat(chat_id: str):
  """
  Get a specific user chat by id

  Returns:
      LLMUserChatResponse
  """
  try:
    user_chat = UserChat.find_by_id(chat_id)
    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

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
def update_chat(chat_id: str, input_chat: ChatUpdateModel):
  """Update a user chat

  Args:
    input_chat (ChatUpdateModel): fields in body of chat to update.
      The only field that can be updated is the title.

  Raises:
    ResourceNotFoundException: If the Chat does not exist
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [JSON]: {'success': 'True'} if the chat is updated,
    NotFoundErrorResponseModel if the chat not found,
    InternalServerErrorResponseModel if the chat update raises an exception
  """
  try:
    input_chat_dict = {**input_chat.dict()}

    existing_chat = UserChat.find_by_id(chat_id)
    for key in input_chat_dict:
      if input_chat_dict.get(key) is not None:
        setattr(existing_chat, key, input_chat_dict.get(key))
    existing_chat.update()

    return {
      "success": True,
      "message": f"Successfully updated user chat {chat_id}",
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


@router.post(
    "",
    name="Create new chat",
    response_model=LLMUserChatResponse)
async def create_user_chat(prompt: Annotated[str, Form()],
                           llm_type: Annotated[str, Form()] = None,
                           chat_file: Union[UploadFile, None] = None,
                           chat_file_url: Annotated[str, Form()] = None,
                           user_data: dict = Depends(validate_token)):
  """
  Create new chat for authentcated user

  Args:
      prompt(str): prompt to initiate chat
      llm_type(str): llm model id
      chat_file(UploadFile): file upload for chat context
      chat_file_url(str): file url for chat context

  Returns:
      LLMUserChatResponse
  """
  llm_type = "VertexAI-Gemini-Flash"

  Logger.info("Creating new chat using"
              f" prompt={prompt} llm_type={llm_type}"
              f" chat_file={chat_file} chat_file_url={chat_file_url}")

  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  # process chat file
  chat_file_type = None
  chat_file_bytes = None
  if chat_file is not None or chat_file_url is not None:
    chat_file_url, chat_file_type = \
        await process_chat_file(chat_file, chat_file_url)
  if chat_file_url is None and chat_file is not None:
    await chat_file.seek(0)
    chat_file_bytes = await chat_file.file.read()

  try:
    user = User.find_by_email(user_data.get("email"))

    # generate text from prompt
    response = await llm_chat(prompt,
                              llm_type,
                              chat_file_type=chat_file_type,
                              chat_file_bytes=chat_file_bytes,
                              chat_file_url=chat_file_url)

    # create new chat for user
    user_chat = UserChat(user_id=user.user_id, llm_type=llm_type,
                         prompt=prompt)
    history = UserChat.get_history_entry(prompt, response)
    user_chat.history = history
    user_chat.save()

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    return {
        "success": True,
        "message": "Successfully created chat",
        "data": chat_data
    }
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/{chat_id}/generate",
    name="Generate new chat response",
    response_model=LLMUserChatResponse)
async def user_chat_generate(chat_id: str, gen_config: LLMChatModel):
  """
  Continue chat based on context of user chat

  Args:
      gen_config: Input config dictionary,
        including prompt(str) and llm_type(str) type for model

  Returns:
      LLMUserChatResponse
  """
  genconfig_dict = {**gen_config.dict()}
  Logger.info(f"Generating new chat response for chat_id={chat_id},"
              f"genconfig_dict={genconfig_dict}")
  response = []

  prompt = genconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  # fetch user chat
  user_chat = UserChat.find_by_id(chat_id)
  if user_chat is None:
    raise ResourceNotFoundException(f"Chat {chat_id} not found ")

  # set llm type for chat
  llm_type = genconfig_dict.get("llm_type", None)
  if llm_type is None:
    llm_type = user_chat.llm_type or DEFAULT_CHAT_LLM_TYPE

  try:
    response = await llm_chat(prompt, llm_type, user_chat)

    # save chat history
    user_chat.update_history(prompt, response)

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
