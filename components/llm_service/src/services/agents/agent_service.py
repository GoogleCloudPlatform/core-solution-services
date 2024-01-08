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
# pylint: disable=consider-using-dict-items,consider-iterating-dictionary,unused-argument

import inspect
import json
import re
from typing import List, Tuple, Dict

from langchain.agents import AgentExecutor
from common.models import BatchJobModel, QueryEngine
from common.models.agent import (AgentCapability,
                                 UserPlan, PlanStep)
from common.utils.errors import ResourceNotFoundException
from common.utils.http_exceptions import BadRequest, InternalServerError
from common.utils.logging_handler import Logger
from config import AGENT_CONFIG_PATH
from config.utils import get_dataset_config
from services.agents import agents
from services.agents.utils import agent_executor_run_with_logs

Logger = Logger.get_logger(__file__)
AGENTS = None

def batch_execute_plan(request_body: Dict, job: BatchJobModel) -> Dict:
  # TODO
  pass

def load_agents(agent_config_path: str):
  global AGENTS
  try:
    agent_config = {}
    with open(agent_config_path, "r", encoding="utf-8") as file:
      agent_config = json.load(file)
    agent_config = agent_config.get("Agents")

    # add agent class and capabilities
    agent_classes = {
      k:klass for (k, klass) in inspect.getmembers(agents)
      if isinstance(klass, type)
    }
    for values in agent_config.values():
      agent_class = agent_classes.get(values["agent_class"])
      values["agent_class"] = agent_class
      values["capabilities"] = [c.value for c in agent_class.capabilities()]

    AGENTS = agent_config
  except Exception as e:
    raise InternalServerError(f" Error loading agent config: {e}") from e

def get_agent_config() -> dict:
  if AGENTS is None:
    load_agents(AGENT_CONFIG_PATH)
  return AGENTS


def get_agent_config_by_name(agent_name: str) -> dict:
  if agent_name in get_agent_config():
    return get_agent_config()[agent_name]
  return {}


def get_model_garden_agent_config() -> dict:
  agent_config = get_agent_config()
  planning_agents = {
      agent: agent_config for agent, agent_config in agent_config.items()
      if AgentCapability.AGENT_PLAN_CAPABILITY.value \
         in agent_config["capabilities"]
  }
  return planning_agents

def get_plan_agent_config() -> dict:
  agent_config = get_agent_config()
  planning_agents = {
      agent: agent_config for agent, agent_config in agent_config.items()
      if AgentCapability.AGENT_PLAN_CAPABILITY.value \
          in agent_config["capabilities"]
  }
  return planning_agents

def get_task_agent_config() -> dict:
  agent_config = get_agent_config()
  planning_agents = {
      agent: agent_config for agent, agent_config in agent_config.items()
      if AgentCapability.AGENT_TASK_CAPABILITY.value \
         in agent_config["capabilities"]
  }
  return planning_agents

def get_all_agents() -> List[dict]:
  """
  Return list of available agents, where each agent is represented
  as a dict of:
    agent_name: {"llm_type": <llm_type>, "capabilities": <capabilities>}
  """
  agent_config = get_agent_config()
  agent_config.update(get_plan_agent_config())
  agent_list = [
    {
      agent: {
        "llm_type": values["llm_type"],
        "capabilities": values["capabilities"],
      }
    }
    for agent, values in agent_config.items()
  ]
  return agent_list


async def run_intent(
    agent_name: str, prompt: str, chat_history:List = None) -> dict:
  """
  Evaluate a prompt to get the intent with best matched route.

  Args:
      prompt(str): the user input prompt
      agent_name(str): the name of the routing agent
      chat_history(List): any previous chat history for context

  Returns:
      output(str): the output of the agent on the user input
      action_steps: the list of action steps take by the agent for the run
  """

  Logger.info(f"Running dispatch "
              f"with prompt=[{prompt}] and "
              f"chat_history=[{chat_history}]")

  agent_params = get_agent_config()[agent_name]
  llm_service_agent = agent_params["agent_class"](agent_params["llm_type"])

  langchain_agent = llm_service_agent.load_agent()
  agent_executor = AgentExecutor.from_agent_and_tools(
      agent=langchain_agent, tools=[])

  intent_list_str = ""
  intent_list = [
    f"- {AgentCapability.AGENT_CHAT_CAPABILITY.value}" \
    " to to perform generic chat conversation.",
    f"- {AgentCapability.AGENT_PLAN_CAPABILITY.value}" \
    " to compose, generate or create a plan.",
  ]
  for intent in intent_list:
    intent_list_str += \
      intent + "\n"

  # Collect all query engines with their description as topics.
  query_engines = QueryEngine.collection.fetch()
  for qe in query_engines:
    intent_list_str += \
      f"- [{AgentCapability.AGENT_QUERY_CAPABILITY.value}:{qe.name}]" \
      f" to run a query on a search engine for information (not raw data)" \
      f" on the topics of {qe.description} \n"

  # Collect all datasets with their descriptions as topics
  datasets = get_dataset_config()
  for ds_name, ds_config in datasets.items():
    if ds_name in ["default"]:
      continue

    description = ds_config["description"]
    intent_list_str += \
      f"- [{AgentCapability.AGENT_DATABASE_CAPABILITY.value}:{ds_name}]" \
      f" to run a query against a database for data related to " \
      f"these areas: {description} \n"

  dispatch_prompt = f"""
    An AI Routing Assistant has access to the following routes:
    {intent_list_str}
    Choose one route based on the question below:
    """
  Logger.info(f"dispatch_prompt: \n{dispatch_prompt}")

  agent_inputs = {
    "input": dispatch_prompt + prompt,
    "chat_history": []
  }

  Logger.info("Running agent executor to get bested matched route.... ")
  output = agent_executor.run(agent_inputs)
  Logger.info(f"Agent {agent_name} generated output=[{output}]")

  agent_logs = output
  Logger.info(f"run_intent - agent_logs: \n{agent_logs}")

  routes = parse_output("Route:", output) or []
  Logger.info(f"Output routes: {routes}")

  # If no best route(s) found, pass to Chat agent.
  if not routes or len(routes) == 0:
    return AgentCapability.AGENT_CHAT_CAPABILITY.value, agent_logs

  # TODO: Refactor this with RoutingAgentOutputParser
  # Get the route for the best matched (first) returned routes.
  route, detail = parse_step(routes[0])[0]
  Logger.info(f"route: {route}, {detail}")

  return route, agent_logs


async def run_agent(agent_name:str,
                    prompt:str,
                    chat_history:List = None) -> str:
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
  Logger.info(f"Running {agent_name} agent "
              f"with prompt=[{prompt}] and "
              f"chat_history=[{chat_history}]")
  agent_params = get_agent_config()[agent_name]
  llm_service_agent = agent_params["agent_class"](agent_params["llm_type"])

  tools = llm_service_agent.get_tools()
  tools_str = ", ".join(tool.name for tool in tools)

  Logger.info(f"Available tools=[{tools_str}]")
  langchain_agent = llm_service_agent.load_agent()

  agent_executor = AgentExecutor.from_agent_and_tools(
      agent=langchain_agent, tools=tools)

  chat_history = chat_history or []
  agent_inputs = {
    "input": prompt,
    "chat_history": chat_history
  }

  Logger.info("Running agent executor.... ")
  output = agent_executor.run(agent_inputs)
  Logger.info(f"Agent {agent_name} generated"
              f" output=[{output}]")
  return output


async def agent_plan(agent_name:str,
                     prompt:str,
                     user_id:str,
                     chat_history:List = None) -> Tuple[str, UserPlan]:
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
  Logger.info(f"Starting with plan for "
              f"agent_name=[{agent_name}], "
              f"prompt=[{prompt}], user_id=[{user_id}], "
              f"chat_history=[{chat_history}]")
  planning_agents = get_plan_agent_config()
  if not agent_name in planning_agents.keys():
    raise BadRequest(f"{agent_name} is not a planning agent.")

  output = await run_agent(agent_name, prompt, chat_history)

  raw_plan_steps = parse_output("Plan:", output)

  # create user plan
  print(f"user_id = {user_id}")

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

  Logger.info(f"Created steps using plan_agent_name=[{agent_name}] "
              f"raw_plan_steps={raw_plan_steps}")
  return output, user_plan


def parse_output(header: str, text: str) -> List[str]:
  """
  Parse plan steps from agent output
  """
  Logger.info(f"Parsing agent output: {header}, {text}")

  # Regex pattern to match the steps after 'Plan:'
  # We are using the re.DOTALL flag to match across newlines and
  # re.MULTILINE to treat each line as a separate string
  steps_regex = re.compile(
      r"^\s*[\d#]+\..+?(?=\n\s*\d+|\Z)", re.MULTILINE | re.DOTALL)

  # Find the part of the text after 'Plan:'
  plan_part = re.split(header, text, flags=re.IGNORECASE)[-1]

  # Find all the steps within the 'Plan:' part
  steps = steps_regex.findall(plan_part)

  # strip whitespace
  steps = [step.strip() for step in steps]

  return steps

def parse_step(text:str) -> dict:
  step_regex = re.compile(
      r"[\d|#]+\.\s.*\[(.*)\]\s?(.*)", re.DOTALL)
  matches = step_regex.findall(text)
  return matches

def agent_execute_plan(
    agent_name:str, prompt:str, user_plan:UserPlan = None) -> str:
  """
  Execute a given plan_steps.
  """
  Logger.info(f"Running {agent_name} agent "
              f"with prompt=[{prompt}] and "
              f"user_plan=[{user_plan}]")
  agent_params = get_agent_config()[agent_name]
  llm_service_agent = agent_params["agent_class"](agent_params["llm_type"])
  agent = llm_service_agent.load_agent()

  tools = llm_service_agent.get_tools()
  tools_str = ", ".join(tool.name for tool in tools)

  Logger.info(f"Available tools=[{tools_str}]")

  plan_steps = []
  for step in user_plan.plan_steps:
    description = PlanStep.find_by_id(step).description
    plan_steps.append(description)

  agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True)

  # langchain StructedChatAgent takes only one input called input
  plan_steps_string = "".join(plan_steps)
  agent_inputs = {
    "input": prompt +plan_steps_string
  }
  Logger.info(f"Running agent executor.... input:{agent_inputs['input']} ")

  # collect print-output to the string.
  output, agent_logs = agent_executor_run_with_logs(
      agent_executor, agent_inputs)

  Logger.info(f"Agent {agent_name} generated"
              f" output=[{output}]")
  return output, agent_logs


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
  agent_config = get_agent_config()
  for agent in agent_config.keys():
    if agent_name == agent:
      return agent_config[agent]["llm_type"]
  raise ResourceNotFoundException(f"can't find agent name {agent_name}")
