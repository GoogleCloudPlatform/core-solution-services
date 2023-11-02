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

""" Agent classes """
# pylint: disable=unused-import

from abc import ABC, abstractmethod
import re
from typing import Union, Type, Callable, List
from config import LANGCHAIN_LLM
from common.utils.http_exceptions import InternalServerError
from langchain.agents import (Agent, AgentOutputParser,
                             ConversationalAgent, ZeroShotAgent)
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS
from services.agent_prompts import (PREFIX, PLANNING_PREFIX,
                                    PLAN_FORMAT_INSTRUCTIONS)
from services.agent_tools import (medicaid_eligibility_requirements,
                                  medicaid_crm_retrieve,
                                  medicaid_crm_update,
                                  medicaid_policy_retrieve,
                                  gmail_tool, docs_tool, calendar_tool)

class BaseAgent(ABC):
  """
  Base Agent for LLM Service agents.  All agents are based on Langchain
  agents and basically specify the configuration for a particular variant
  of Langchain agent.
  """

  llm_type: str = None
  """ the LLM Service llm type used to power the agent """

  agent: Agent = None
  """ the langchain agent instance """

  agent_class: Type[Agent] = None
  """ the langchain agent class """

  name:str = None
  """ The name of the agent """

  def __init__(self, llm_type: str):
    self.llm_type = llm_type
    self.agent = None

  @property
  def prefix(self) -> str:
    return PREFIX

  @property
  def format_instructions(self) -> str:
    return FORMAT_INSTRUCTIONS

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    raise NotImplementedError(
        "Derived classes should provide output_parser_class")

  @abstractmethod
  def get_tools(self) -> List[Callable]:
    """ return tools used by this agent """

  def load_agent(self) -> Agent:
    """ load this agent and return an instance of langchain Agent"""
    tools = self.get_tools()

    llm = LANGCHAIN_LLM.get(self.llm_type)
    if llm is None:
      raise InternalServerError(
          f"MediKateAgent: cannot find LLM type {self.llm_type}")

    output_parser = self.output_parser_class()

    self.agent = self.agent_class.from_llm_and_tools(
        llm=llm,
        tools=tools,
        prefix=self.prefix,
        format_instructions=self.format_instructions,
        output_parser=output_parser
    )
    return self.agent


class MediKateAgent(BaseAgent):
  """
  MediKate Agent.  A constituent facing agent designed to assist
  state residents with enrolling in Medicaid.
  """

  def __init__(self, llm_type: str):
    super().__init__(llm_type)
    self.name = "MediKate"
    self.agent_class = ConversationalAgent

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    return ToolAgentOutputParser

  def get_tools(self):
    tools = [medicaid_eligibility_requirements]
    return tools


class CaseyPlanAgent(BaseAgent):
  """
  Casey Plan Agent.  This is an agent configured to make plans.
  Plans will be executed using a different agent.
  """

  def __init__(self, llm_type: str):
    super().__init__(llm_type)
    self.name = "CaseyPlanner"
    self.agent_class = ConversationalAgent

  @property
  def prefix(self) -> str:
    return PLANNING_PREFIX

  @property
  def format_instructions(self) -> str:
    return PLAN_FORMAT_INSTRUCTIONS

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    return PlanningAgentOutputParser

  def get_tools(self):
    tools = [medicaid_eligibility_requirements, medicaid_crm_retrieve,
             medicaid_policy_retrieve, gmail_tool, docs_tool, calendar_tool]
    return tools


class CaseyAgent(BaseAgent):
  """
  Casey Agent. This is an agent configured to execute plans as well
  as a general info retrieval agent.
  """

  def __init__(self, llm_type: str):
    super().__init__(llm_type)
    self.name = "Casey"
    self.agent_class = ConversationalAgent

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    return ToolAgentOutputParser

  def get_planning_agent(self) -> str:
    return "CaseyPlanner"

  def get_tools(self):
    tools = [medicaid_eligibility_requirements, medicaid_crm_update]
    return tools


class PlanningAgentOutputParser(AgentOutputParser):
  """Output parser for a agent that makes plans."""

  ai_prefix: str = "AI"
  """Prefix to use before AI output."""

  def get_format_instructions(self) -> str:
    return PLAN_FORMAT_INSTRUCTIONS

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
    return "zero_shot"


class ToolAgentOutputParser(AgentOutputParser):
  """Output parser for a conversational agent that uses tools."""

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
