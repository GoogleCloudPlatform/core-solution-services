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

import re
from typing import Union, List
from common.models.agent import Agent, AgentType
from common.utils.http_exceptions import InternalServerError
from common.utils.errors import ResourceNotFoundException
from config import LANGCHAIN_LLM, VERTEX_LLM_TYPE_BISON_CHAT
from langchain.agents import (Agent as LangChainAgent, AgentOutputParser,
                              ConversationalAgent, AgentExecutor)
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS
from services.agent_prompts import PREFIX
from services.agent_tools import medicaid_eligibility_requirements


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

def run_agent(agent_name:str, prompt:str, chat_history:List=[]) -> str:
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


class MediKateAgent:
  """
  MediKate Agent
  """

  llm_type: str = None
  """ the LLM Service llm type used to power the agent """

  agent: ConversationalAgent = None
  """ the langchain agent instance """

  name:str = "MediKate"
  """ The name of the agent """

  def __init__(self, llm_type: str):
    self.llm_type = llm_type
    self.agent = None
    self.name = "MediKate"

  def load_agent(self) -> LangChainAgent:
    """ load this agent and return an instance of langchain Agent"""
    tools = self.get_tools()

    llm = LANGCHAIN_LLM.get(self.llm_type)
    if llm is None:
      raise InternalServerError(
          f"MediKateAgent: cannot find LLM type {self.llm_type}")

    output_parser = MediKateConvoOutputParser()

    self.agent = ConversationalAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        output_parser=output_parser,
        prefix=PREFIX
    )
    return self.agent

  def get_tools(self):
    tools = [medicaid_eligibility_requirements]
    return tools


class MediKateConvoOutputParser(AgentOutputParser):
  """Output parser for the conversational agent."""

  ai_prefix: str = "AI"
  """Prefix to use before AI output."""

  def get_format_instructions(self) -> str:
    return FORMAT_INSTRUCTIONS

  def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
    if f"{self.ai_prefix}:" in text:
      return AgentFinish(
          {"output": text.split(f"{self.ai_prefix}:")[-1].strip()}, text
      )
    regex = r"Action: (.*?)[\n]*Action Input: (.*)"
    match = re.search(regex, text)
    if not match:
      # TODO: undo this temporary fix to make the v1 agent terminate
      #raise OutputParserException(
      #    f"MIRA: Could not parse LLM output: `{text}`")
      return AgentFinish(
          {"output": text.split(f"{self.ai_prefix}:")[-1].strip()}, text
      )
    action = match.group(1)
    action_input = match.group(2)
    return AgentAction(action.strip(),
                       action_input.strip(" ").strip('"'), text)

  @property
  def _type(self) -> str:
    return "conversational"

class MediKateOutputParser(AgentOutputParser):
  """Output parser for custom agent."""

  def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
    llm_output = text
    # Check if agent should finish
    if "Final Answer:" in llm_output:
      return AgentFinish(
        # Return values is generally always a dictionary with a
        # single `output` key
        # It is not recommended to try anything else at the moment :)
        return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
        log=llm_output,
      )
    # Parse out the action and action input
    regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
    match = re.search(regex, llm_output, re.DOTALL)
    if not match:
      raise OutputParserException(f"Could not parse LLM output: `{llm_output}`")
    action = match.group(1).strip()
    action_input = match.group(2)

    # Return the action and action input
    return AgentAction(tool=action,
                       tool_input=action_input.strip(" ").strip('"'),
                       log=llm_output)
  