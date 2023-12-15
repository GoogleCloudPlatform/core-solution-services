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
from common.models import User, UserChat, UserPlan, PlanStep
from common.utils.auth_service import validate_token
from common.utils.logging_handler import Logger
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError,
                                 PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest,
                                          ResourceNotFound)
from schemas.agent_schema import (LLMAgentPlanModel,
                                  LLMAgentPlanResponse,
                                  LLMUserPlanResponse,
                                  LLMAgentPlanRunResponse)
from services.agents.agent_service import (agent_plan,
                                           agent_execute_plan,
                                           get_llm_type_for_agent)
from config import (PAYLOAD_FILE_SIZE, ERROR_RESPONSES)

Logger = Logger.get_logger(__file__)
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
    Logger.info(f"Getting user plan by plan_id={plan_id}")
    user_plan = UserPlan.find_by_id(plan_id)
    plan_data = user_plan.get_fields(reformat_datetime=True)
    plan_data["id"] = user_plan.id

    # Populate plan steps.
    plan_steps = []
    for plan_step_id in plan_data.get("plan_steps", []):
      plan_step = PlanStep.find_by_id(plan_step_id)
      plan_steps.append({
        "id": plan_step_id,
        "description": plan_step.description
      })
    plan_data["plan_steps"] = plan_steps

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
def generate_agent_plan(agent_name: str,
                        plan_config: LLMAgentPlanModel,
                        chat_id: str = None,
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
  Logger.info(f"Running {agent_name} "
              f"agent on {planconfig_dict}")

  prompt = planconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    error_msg = "Missing or invalid payload parameters"
    Logger.error(f"{error_msg}")
    return BadRequest(error_msg)

  if len(prompt) > PAYLOAD_FILE_SIZE:
    error_msg = f"Prompt must be less than {PAYLOAD_FILE_SIZE}"
    Logger.error(f"{error_msg}")
    return PayloadTooLargeError(error_msg)

  try:
    user = User.find_by_email(user_data.get("email"))
    llm_type = get_llm_type_for_agent(agent_name)

    # Generate the plan
    output, user_plan = agent_plan(agent_name, prompt, user.id)

    # create default name for user plan
    now = datetime.now().strftime("%m-%d-%Y %H:%M")
    user_plan.name = f"User {user.id} Plan {agent_name} {now}"
    user_plan.update()

    # Get the existing Chat data or create a new one.
    user_chat = None
    if chat_id:
      user_chat = UserChat.find_by_id(chat_id)

    if not user_chat:
      user_chat = UserChat(user_id=user.user_id, llm_type=llm_type,
                           agent_name=agent_name)
    # Save user chat to retrieve actual ID.
    user_chat.update_history(prompt, output)
    user_chat.save()

    chat_id = user_chat.id
    chat_data = user_chat.get_fields(reformat_datetime=True)
    chat_data["id"] = chat_id

    plan_data = user_plan.get_fields(reformat_datetime=True)
    plan_data["id"] = user_plan.id

    user_chat.update_history(custom_entry={
      "plan": plan_data,
    })

    # return plan steps in summary form with plans and descriptions
    plan_steps = []
    for plan_step_id in plan_data["plan_steps"]:
      plan_step = PlanStep.find_by_id(plan_step_id)
      plan_steps.append({
        "id": plan_step_id,
        "description": plan_step.description
      })
    plan_data["plan_steps"] = plan_steps

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
    name="Start to execute a plan",
    response_model=LLMAgentPlanRunResponse)
async def agent_plan_execute(plan_id: str,
                             chat_id: str = None,
                             agent_name: str = "Task",
                             user_data: dict = Depends(validate_token)):
  """
  Start a plan execution job

  Args:
      LLMPlanModel

  Returns:
      LLMPlanRunResponse
  """
  user_plan = UserPlan.find_by_id(plan_id)
  assert user_plan, f"Unable to find user plan {plan_id}"
  assert user_data, "user_data is not defined."

  # TODO: Add a check whether this plan belongs to a particular
  # user_id.
  try:
    # Get the existing Chat data or create a new one.
    user_chat = None
    if chat_id:
      user_chat = UserChat.find_by_id(chat_id)

    prompt = """Run the plan in the chat history provided below."""
    result, agent_logs = agent_execute_plan(
        agent_name, prompt, user_plan)

    if user_chat:
      user_chat.update_history(
          response=f"Successfully executed plan {plan_id}")
      user_chat.update_history(response=agent_logs)
      user_chat.save()

    Logger.info(result)
    return {
      "success": True,
      "message": f"Successfully executed plan {plan_id}",
      "data": {
        "result": result,
        "agent_logs": agent_logs
      }
    }

  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())

    return {
      "success": False,
      "message": traceback.print_exc(),
    }
