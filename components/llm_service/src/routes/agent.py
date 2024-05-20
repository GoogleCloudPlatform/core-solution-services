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
from common.utils.batch_jobs import initiate_batch_job
from common.utils.errors import (ResourceNotFoundException,
                                 PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest)
from common.utils.config import JOB_TYPE_ROUTING_AGENT, JOB_TYPE_AGENT_RUN
from schemas.agent_schema import (LLMAgentRunResponse,
                                  LLMAgentRunModel,
                                  LLMAgentGetAllResponse,
                                  LLMAgentGetTypeResponse)
from services.agents.agent_service import (get_all_agents, run_agent)
from services.agents.agents import BaseAgent
from services.agents.routing_agent import run_routing_agent, run_intent
from services.langchain_service import langchain_chat_history
from config import (PAYLOAD_FILE_SIZE, ERROR_RESPONSES,
                    PROJECT_ID, DATABASE_PREFIX,
                    ENABLE_OPENAI_LLM, ENABLE_COHERE_LLM,
                    DEFAULT_VECTOR_STORE, PG_HOST, AGENT_CONFIG_PATH)

from config import (PAYLOAD_FILE_SIZE,
                    ERROR_RESPONSES, ENABLE_OPENAI_LLM, ENABLE_COHERE_LLM,
                    DEFAULT_VECTOR_STORE, VECTOR_STORES, PG_HOST,
                    ONEDRIVE_CLIENT_ID, ONEDRIVE_TENANT_ID)

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
  agent_config = get_all_agents()

  # convert config vals to str
  agent_config = {
    agent: {k: str(v) for k, v in ac.items()}
    for agent, ac in agent_config.items()
  }

  try:
    return {
      "success": True,
      "message": "Successfully retrieved agents",
      "data": agent_config
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.get(
    "/{agent_type}",
    name="Get all Agents of a specific type",
    response_model=LLMAgentGetTypeResponse)
def get_agent_types(agent_type: str):
  """
  Get all agents of a specific agent type (which corresponds
  to "agent capability")

  Returns:
      LLMAgentGetTypeResponse
  """
  agent_type = agent_type.lower().capitalize()
  agent_config = BaseAgent.get_agents_by_capability(agent_type)

  # convert config vals to str
  agent_config = {
    agent: {k: str(v) for k, v in ac.items()}
    for agent, ac in agent_config.items()
  }

  try:
    return {
      "success": True,
      "message": "Successfully retrieved agents",
      "data": agent_config
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.post(
    "/dispatch/{agent_name}",
    name="Evaluate user input and choose a dispatch route")
async def run_dispatch(agent_name: str, run_config: LLMAgentRunModel,
                       user_data: dict = Depends(validate_token)):
  """
  Run RoutingAgent with prompt, and pass to corresponding agent,
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
  llm_type = runconfig_dict.get("llm_type")
  db_result_limit = runconfig_dict.get("db_result_limit")
  run_as_batch_job = runconfig_dict.get("run_as_batch_job", False)

  Logger.info(
      f"Agent {agent_name} Choosing route based on {runconfig_dict}")

  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  user = User.find_by_email(user_data.get("email"))
  user_chat = None

  # Retrieve an existing chat or create new chat for user
  if chat_id:
    user_chat = UserChat.find_by_id(chat_id)
  if not user_chat:
    user_chat = UserChat(user_id=user.user_id, prompt=prompt)

  user_chat.update_history(custom_entry={
    f"{CHAT_HUMAN}": prompt,
  })
  user_chat.save()
  chat_data = user_chat.get_fields(reformat_datetime=True)
  chat_data["id"] = user_chat.id

  # Get route as early as possible.
  route, route_logs = await run_intent(
    agent_name, prompt, chat_history=user_chat.history)
  route_parts = route.split(":", 1)
  route_type = route_parts[0]

  # create default chat_history_entry
  user_chat.update_history(custom_entry={
    "route": route_type,
    "route_name": route,
    "route_logs": route_logs,
  })
  user_chat.save()

  if run_as_batch_job:
    # Execute routing agent as batch_job and return job detail.
    data = {
      "prompt": prompt,
      "agent_name": agent_name,
      "user_id": user.id,
      "chat_id": user_chat.id,
      "llm_type": llm_type,
      "route": route,
    }
    if db_result_limit:
      data["db_result_limit"] = db_result_limit

    env_vars = {
      "DATABASE_PREFIX": DATABASE_PREFIX,
      "PROJECT_ID": PROJECT_ID,
      "ENABLE_OPENAI_LLM": str(ENABLE_OPENAI_LLM),
      "ENABLE_COHERE_LLM": str(ENABLE_COHERE_LLM),
      "DEFAULT_VECTOR_STORE": str(DEFAULT_VECTOR_STORE),
      "PG_HOST": PG_HOST,
      "AGENT_CONFIG_PATH": AGENT_CONFIG_PATH,
    }
    response = initiate_batch_job(data, JOB_TYPE_ROUTING_AGENT, env_vars)
    Logger.info(f"Batch job response: {response}")
    return {
      "success": True,
      "message": "Successfully ran dispatch in batch mode",
      "data": {
        "route": route_type,
        "route_name": route,
        "chat": chat_data,
        "batch_job": response["data"],
      },
    }

  else:
    # Execute routing agent synchronously.
    route, response_data = await run_routing_agent(
        prompt, agent_name, user, user_chat, llm_type,
        db_result_limit=db_result_limit, route=route)

    response_data["route"] = route_type
    response_data["route_name"] = route

    return {
      "success": True,
      "message": "Successfully ran dispatch",
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

  run_as_batch_job = runconfig_dict.get("run_as_batch_job", False)
  Logger.info(f"run_as_batch_job = {run_as_batch_job}")

  user = User.find_by_email(user_data.get("email"))
  llm_type = BaseAgent.get_llm_type_for_agent(agent_name)
  runconfig_dict["user_email"] = user.email

  if run_as_batch_job:
    # create new chat for user
    user_chat = UserChat(user_id=user.user_id, prompt=prompt,
                         llm_type=llm_type, agent_name=agent_name)
    # Save user chat to retrieve actual ID.
    user_chat.update_history(prompt, output)
    user_chat.save()

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    # launch batch job to perform query
    try:
      data = {
        "agent_name": agent_name,
        "prompt": prompt,
        "llm_type": llm_type,
        "user_id": user.id,
        "user_chat_id": user_chat.id,
        "dataset": runconfig_dict["dataset"]
      }
      env_vars = {
        "DATABASE_PREFIX": DATABASE_PREFIX,
        "PROJECT_ID": PROJECT_ID,
        "ENABLE_OPENAI_LLM": str(ENABLE_OPENAI_LLM),
        "ENABLE_COHERE_LLM": str(ENABLE_COHERE_LLM),
        "DEFAULT_VECTOR_STORE": str(DEFAULT_VECTOR_STORE),
        "PG_HOST": PG_HOST,
      }
      response = initiate_batch_job(data, JOB_TYPE_AGENT_RUN, env_vars)
      Logger.info(f"Batch job response: {response}")

      return {
        "success": True,
        "message": "Successfully ran query in batch mode",
        "data": {
          "query": query_data,
          "batch_job": response["data"],
        },
      }
    except Exception as e:
      Logger.error(e)
      Logger.error(traceback.print_exc())
      raise InternalServerError(str(e)) from e

  # normal sync execution
  try:
    output, agent_logs = \
        await run_agent(agent_name, prompt, None, runconfig_dict)
    Logger.info(f"Generated output=[{output}]")

    # create new chat for user
    user_chat = UserChat(user_id=user.user_id, prompt=prompt,
                         llm_type=llm_type, agent_name=agent_name)
    # Save user chat to retrieve actual ID.
    user_chat.update_history(prompt, output)
    user_chat.save()

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    if "db_result" in output or "route" in output:
      response_data = output
    else:
      response_data = {
        "content": output,
        "chat": chat_data,
        "agent_logs": agent_logs
      }
  
    response = {
      "success": True,
      "message": "Successfully ran agent",
      "data": response_data
    }
    
    Logger.info(
      f"run agent prompt=[{prompt}] agent=[{agent_name}]"
      f" response [{response}]")
    
    return response
    
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/run/{agent_name}/{chat_id}",
    name="Run agent on user input with chat history",
    response_model=LLMAgentRunResponse)
async def agent_run_chat(agent_name: str, chat_id: str,
                         run_config: LLMAgentRunModel,
                         user_data: dict = Depends(validate_token)):
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
    user = User.find_by_email(user_data.get("email"))
    runconfig_dict["user_email"] = user.email
    chat_history = langchain_chat_history(user_chat)
    output, agent_logs = \
        await run_agent(agent_name, prompt, chat_history, runconfig_dict)
    Logger.info(f"Generated output=[{output}]")

    # save chat history
    user_chat.update_history(prompt, output)

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    if "db_result" in output or "route" in output:
      response_data = output
    else:
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
