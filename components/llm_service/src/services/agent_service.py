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

from typing import List
from common.models.agent import AgentType
from common.utils.errors import ResourceNotFoundException
from config import VERTEX_LLM_TYPE_BISON_CHAT
from langchain.agents import AgentExecutor
from services.agents import MediKateAgent

AGENTS = {
  "MediKate": {
    "llm_type": VERTEX_LLM_TYPE_BISON_CHAT,
    "agent_type": AgentType.LANGCHAIN_CONVERSATIONAL,
    "agent_class": MediKateAgent
  }
}

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
  for agent in AGENTS:
    if agent_name == agent["agent_name"]:
      return agent["llm_type"]
  raise ResourceNotFoundException(f"can't find agent name {agent_name}")
  