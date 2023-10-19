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

# pylint: disable = broad-except,unused-import

""" Agent endpoints """
import traceback
from typing import Optional
from fastapi import APIRouter
from common.utils.logging_handler import Logger
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError,
                                 PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest,
                                          ResourceNotFound, PayloadTooLarge)
from schemas.agent_schema import (LLMAgentRunResponse,
                                 LLMAgentRunModel,
                                 LLMAgentGetAllResponse)
from services.agent_service import get_all_agents, MediKateAgent
from langchain.agents import AgentExecutor
from config import (PAYLOAD_FILE_SIZE, ERROR_RESPONSES,
                    VERTEX_LLM_TYPE_BISON_CHAT)

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
    "/run/{agent_id}",
    name="Run agent on user input",
    response_model=LLMAgentRunResponse)
def run_agent(agent_id: str, run_config: LLMAgentRunModel):
  """
  Run agent on user input

  Args:
      agent_id(str): Agent ID
      run_config(LLMAgentRunModel): the config of the Agent model.

  Returns:
      LLMAgentRunResponse
  """
  runconfig_dict = {**run_config.dict()}

  prompt = runconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  medikate_agent = MediKateAgent(VERTEX_LLM_TYPE_BISON_CHAT)

  tools = medikate_agent.get_tools()
  agent = medikate_agent.load_agent()

  agent_executor = AgentExecutor.from_agent_and_tools(
      agent=agent, tools=tools)

  agent_inputs = {
    "input": prompt,
    "chat_history": []
  }

  output = agent_executor.run(agent_inputs)

  try:

    return {
        "success": True,
        "message": "Successfully ran agent",
        "content": output
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


