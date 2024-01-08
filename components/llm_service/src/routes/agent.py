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

""" Agent endpoints """
import traceback
from fastapi import APIRouter, Depends
from common.models import User, UserChat
from common.models.llm import CHAT_HUMAN
from common.utils.auth_service import validate_token
from common.utils.logging_handler import Logger
from common.utils.errors import (ResourceNotFoundException,
                                 PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest)
from schemas.agent_schema import (LLMAgentRunResponse,
                                 LLMAgentRunModel,
                                 LLMAgentGetAllResponse)
from services.agents.agent_service import (get_all_agents, run_agent,
                                          get_llm_type_for_agent)
from services.agents.routing_agent import run_routing_agent
from services.langchain_service import langchain_chat_history
from config import (PAYLOAD_FILE_SIZE, ERROR_RESPONSES)

Logger = Logger.get_logger(__file__)
router = APIRouter(prefix="/agent", tags=["Agents"], responses=ERROR_RESPONSES)

@router.get(
    "",
    name="Get all Agents",
    response_model=LLMAgentGetAllResponse)
def get_agents():
  """
  Get all agents defined in the LLM Service

  Returns:
      LLMGetAgentResponse
  """
  agents = get_all_agents()

  try:
    return {
      "success": True,
      "message": "Successfully retrieved agents",
      "data": agents
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.post(
    "/dispatch/{agent_name}",
    name="Evaluate user input and choose a dispatch route")
async def run_dispatch(agent_name: str, run_config: LLMAgentRunModel,
                       user_data: dict = Depends(validate_token)):
  """
  Run DispatchAgent with prompt, and pass to corresponding agent,
  e.g. Chat, Plan or Query.

  Args:
      agent_name(str): Agent name
      run_config(LLMAgentRunModel): the config of the Agent model.

  Returns:
      LLMAgentRunResponse
  """
  runconfig_dict = {**run_config.dict()}
  prompt = runconfig_dict.get("prompt")
  chat_id = runconfig_dict.get("chat_id")
  Logger.info(f"Choosing a dispatch route based on {runconfig_dict}")

  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  user = User.find_by_email(user_data.get("email"))
  user_chat = None

  # Retrieve an existing chat or create new chat for user
  if chat_id:
    user_chat = UserChat.find_by_id(chat_id)
  if not user_chat:
    user_chat = UserChat(user_id=user.user_id)

  user_chat.update_history(custom_entry={
    f"{CHAT_HUMAN}": prompt,
  })
  user_chat.save()

  # execute routing agent
  route, response_data = run_routing_agent(prompt, agent_name, user_chat, user)

  return {
    "success": True,
    "message": "Successfully ran dispatch",
    "route": route,
    "data": response_data
  }


@router.post(
    "/run/{agent_name}",
    name="Run agent on user input",
    response_model=LLMAgentRunResponse)
async def agent_run(agent_name: str,
              run_config: LLMAgentRunModel,
              user_data: dict = Depends(validate_token)):
  """
  Run agent on user input. Store history in new UserChat.

  Args:
      agent_name(str): Agent name
      run_config(LLMAgentRunModel): the config of the Agent model.

  Returns:
      LLMAgentRunResponse
  """
  runconfig_dict = {**run_config.dict()}

  Logger.info(f"Running {agent_name} agent on {runconfig_dict}")

  prompt = runconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  try:
    user = User.find_by_email(user_data.get("email"))
    llm_type = get_llm_type_for_agent(agent_name)

    output, agent_logs = await run_agent(agent_name, prompt)
    Logger.info(f"Generated output=[{output}]")

    # create new chat for user
    user_chat = UserChat(user_id=user.user_id, llm_type=llm_type,
                           agent_name=agent_name)
    # Save user chat to retrieve actual ID.
    user_chat.update_history(prompt, output)
    user_chat.save()

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    response_data = {
      "content": output,
      "chat": chat_data,
      "agent_logs": agent_logs
    }

    return {
      "success": True,
      "message": "Successfully ran agent",
      "data": response_data
    }
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

@router.post(
    "/run/{agent_name}/{chat_id}",
    name="Run agent on user input with chat history",
    response_model=LLMAgentRunResponse)
async def agent_run_chat(agent_name: str, chat_id: str,
                   run_config: LLMAgentRunModel):
  """
  Run agent on user input with prior chat history

  Args:
      agent_name(str): Agent ID
      run_config(LLMAgentRunModel): the config of the Agent model.

  Returns:
      LLMAgentRunResponse
  """
  runconfig_dict = {**run_config.dict()}
  Logger.info(f"Running agent {agent_name} on user input {runconfig_dict} "
              f"with chat history with "
              f"chat_id = {chat_id}.")
  prompt = runconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  # fetch user chat
  user_chat = UserChat.find_by_id(chat_id)
  if user_chat is None:
    raise ResourceNotFoundException(f"Chat {chat_id} not found ")

  try:
    # run agent to get output
    chat_history = langchain_chat_history(user_chat)
    output = await run_agent(agent_name, prompt, chat_history)
    Logger.info(f"Generated output=[{output}]")

    # save chat history
    user_chat.update_history(prompt, output)

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    response_data = {
      "content": output,
      "chat": chat_data,
    }

    return {
        "success": True,
        "message": "Successfully ran agent",
        "data": response_data
    }
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e
