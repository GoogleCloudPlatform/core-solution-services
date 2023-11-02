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
from datetime import datetime
import traceback
from fastapi import APIRouter, Depends
from common.models import User, UserChat, UserPlan
from common.utils.auth_service import validate_token
from common.utils.batch_jobs import initiate_batch_job
from common.utils.config import JOB_TYPE_AGENT_PLAN_EXECUTE
from common.utils.logging_handler import Logger
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError,
                                 PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest,
                                          ResourceNotFound)
from common.schemas.batch_job_schemas import BatchJobModel
from schemas.agent_schema import (LLMAgentPlanModel,
                                  LLMAgentPlanResponse,
                                  LLMUserPlanResponse)
from services.agent_service import (agent_plan,
                                    get_llm_type_for_agent)
from config import (PAYLOAD_FILE_SIZE, ERROR_RESPONSES, PROJECT_ID)

router = APIRouter(prefix="/agent/plan", tags=["Agent Plans"],
                   responses=ERROR_RESPONSES)

@router.get(
    "/{plan_id}",
    name="Get user plan",
    response_model=LLMUserPlanResponse)
def get_plan(plan_id: str):
  """
  Get a specific user plan by id

  Returns:
      LLMUserPlanResponse
  """
  try:
    user_plan = UserPlan.find_by_id(plan_id)
    plan_data = user_plan.get_fields(reformat_datetime=True)
    plan_data["id"] = user_plan.id

    return {
      "success": True,
      "message": f"Successfully retrieved user plan {plan_id}",
      "data": plan_data
    }
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/{agent_name}",
    name="Generate a plan by agent on user input",
    response_model=LLMAgentPlanResponse)
def generate_agent_plan(agent_name: str, plan_config: LLMAgentPlanModel,
                        user_data: dict = Depends(validate_token)):
  """
  Run agent on user input to generate a plan.
  Store plan in new UserPlan.
  Store history in new UserChat.

  Args:
      agent_name(str): Agent name
      plan_config(LLMAgentPlanModel): the config of the Agent model.

  Returns:
      LLMAgentPlanResponse
  """
  planconfig_dict = {**plan_config.dict()}

  prompt = planconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  try:
    user = User.find_by_email(user_data.get("email"))
    llm_type = get_llm_type_for_agent(agent_name)

    output, user_plan = agent_plan(agent_name, prompt, user.id)

    # create default name for user plan
    now = datetime.now().strftime("%m-%d-%Y %H:%M")
    user_plan.name = f"User {user.id} Plan {agent_name} {now}"
    user_plan.update()

    # create new chat for user
    user_chat = UserChat(user_id=user.user_id, llm_type=llm_type,
                         agent_name=agent_name)
    history = UserChat.get_history_entry(prompt, output)
    user_chat.history = history
    user_chat.save()

    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = user_chat.id

    plan_data = user_plan.get_fields(reformat_datetime=True)
    plan_data["id"] = user_plan.id

    response = {
      "content": output,
      "chat": chat_data,
      "plan": plan_data
    }

    return {
      "success": True,
      "message": "Successfully ran agent",
      "data": response
    }
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

@router.post(
    "/{plan_id}/run",
    name="Start a batch job to execute a plan",
    response_model=BatchJobModel)
async def agent_plan_execute(plan_id: str,
                             user_data: dict = Depends(validate_token)):
  """
  Start a plan execution job

  Args:
      LLMPlanModel

  Returns:
      LLMPlanRunResponse
  """
  user_id = user_data.get("user_id")

  try:
    data = {
      "plan_id": plan_id,
      "user_id": user_id
    }
    env_vars = {
      "PROJECT_ID": PROJECT_ID
    }
    response = initiate_batch_job(data, JOB_TYPE_AGENT_PLAN_EXECUTE, env_vars)
    Logger.info(response)
    return response
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e
