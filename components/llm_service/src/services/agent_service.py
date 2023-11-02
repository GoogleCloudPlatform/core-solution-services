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

""" Agent service """
# pylint: disable=consider-using-dict-items,consider-iterating-dictionary,unused-import

import re
from typing import List, Tuple
from common.models.agent import AgentType, UserPlan, PlanStep
from common.utils.errors import ResourceNotFoundException
from common.utils.http_exceptions import BadRequest
from common.utils.logging_handler import Logger
from config import (VERTEX_LLM_TYPE_BISON_CHAT,
                    OPENAI_LLM_TYPE_GPT3_5,
                    OPENAI_LLM_TYPE_GPT4)
from langchain.agents import AgentExecutor
from services.agents import MediKateAgent, CaseyAgent, CaseyPlanAgent

AGENTS = {
  "MediKate": {
    "llm_type": VERTEX_LLM_TYPE_BISON_CHAT,
    "agent_type": AgentType.LANGCHAIN_CONVERSATIONAL,
    "agent_class": MediKateAgent
  },
  "Casey": {
    "llm_type": VERTEX_LLM_TYPE_BISON_CHAT,
    "agent_type": AgentType.LANGCHAIN_CONVERSATIONAL,
    "agent_class": CaseyAgent
  },
  "CaseyPlanner": {
    "llm_type": OPENAI_LLM_TYPE_GPT4,
    "agent_type": AgentType.LANGCHAIN_ZERO_SHOT,
    "agent_class": CaseyPlanAgent
  }
}

PLANNING_AGENTS = [
  "Casey"
]

def get_all_agents() -> List[dict]:
  """
  Return list of available agents, where each agent is represented
  as a dict of:
    agent_type: llm_type
  """
  agent_list = [
    {agent: values["llm_type"]}
    for agent, values in AGENTS.items()
  ]
  return agent_list

def run_agent(agent_name:str, prompt:str, chat_history:List = None) -> str:
  """
  Run an agent on user input

  Args:
      agent_name(str): Agent name
      prompt(str): the user input prompt
      chat_history(List): any previous chat history for context

  Returns:
      output(str): the output of the agent on the user input
      action_steps: the list of action steps take by the agent for the run
  """
  agent_params = AGENTS[agent_name]
  llm_service_agent = agent_params["agent_class"](agent_params["llm_type"])

  tools = llm_service_agent.get_tools()
  langchain_agent = llm_service_agent.load_agent()

  agent_executor = AgentExecutor.from_agent_and_tools(
      agent=langchain_agent, tools=tools)

  chat_history = chat_history or []
  agent_inputs = {
    "input": prompt,
    "chat_history": chat_history
  }

  output = agent_executor.run(agent_inputs)

  return output


def agent_plan(agent_name:str, prompt:str,
               user_id:str, chat_history:List = None) -> Tuple[str, UserPlan]:
  """
  Run an agent on user input to generate a plan

  Args:
      agent_name(str): Agent name
      prompt(str): the user input prompt
      chat_history(List): any previous chat history for context

  Returns:
      output(str): the output of the agent on the user input
      user_plan(str): user plan object created from agent plan
  """
  if not agent_name in PLANNING_AGENTS:
    raise BadRequest(f"{agent_name} is not a planning agent.")

  # get LLM service agent
  agent_params = AGENTS[agent_name]
  llm_service_agent = agent_params["agent_class"](agent_params["llm_type"])

  plan_agent_name = llm_service_agent.get_planning_agent()

  output = run_agent(plan_agent_name, prompt, chat_history)

  raw_plan_steps = parse_plan(output)

  # create user plan
  user_plan = UserPlan(user_id=user_id, agent_name=agent_name)
  user_plan.save()

  # create PlanStep models
  plan_steps = [
      PlanStep(user_id=user_id,
               plan_id=user_plan.id,
               description=step_description,
               agent_name=agent_name)
      for step_description in raw_plan_steps]
  plan_step_ids = []
  for step in plan_steps:
    step.save()
    plan_step_ids.append(step.id)

  # save plan steps
  user_plan.plan_steps = plan_step_ids
  user_plan.update()

  return output, user_plan


def parse_plan(text: str) -> List[str]:
  """
  Parse plan steps from agent output
  """
  Logger.info(f"agent plan output {text}")

  # Regex pattern to match the steps after 'Plan:'
  # We are using the re.DOTALL flag to match across newlines and
  # re.MULTILINE to treat each line as a separate string
  steps_regex = re.compile(
      r"^\s*\d+\..+?(?=\n\s*\d+|\Z)", re.MULTILINE | re.DOTALL)

  # Find the part of the text after 'Plan:'
  plan_part = re.split(r"Plan:", text, flags=re.IGNORECASE)[-1]

  # Find all the steps within the 'Plan:' part
  steps = steps_regex.findall(plan_part)

  # strip whitespace
  steps = [step.strip() for step in steps]

  return steps


def batch_execute_plan():
  pass


def get_llm_type_for_agent(agent_name: str) -> str:
  """
  Return agent llm_type given agent name

  Args:
    agent_name: str
  Returns:
    llm_type: str
  Raises:
    ResourceNotFoundException if agent_name not found
  """
  for agent in AGENTS.keys():
    if agent_name == agent:
      return AGENTS[agent]["llm_type"]
  raise ResourceNotFoundException(f"can't find agent name {agent_name}")
  