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
import re
from abc import ABC, abstractmethod
from typing import Union, Type, Callable, List, Optional

from langchain.agents import Agent as LangchainAgent
from langchain.agents import (AgentOutputParser,
                              ConversationalAgent)
from langchain.agents.structured_chat.base import StructuredChatAgent
from langchain.agents.structured_chat.output_parser \
    import StructuredChatOutputParserWithRetries
from langchain.agents.structured_chat.prompt \
    import FORMAT_INSTRUCTIONS as STRUCTURED_FORMAT_INSTRUCTIONS
from langchain.agents.conversational.prompt import FORMAT_INSTRUCTIONS
from langchain.schema import AgentAction, AgentFinish
from config.utils import get_dataset_config, get_agent_config, get_config_list
from common.models import QueryEngine
from common.models.agent import AgentCapability
from common.utils.errors import ResourceNotFoundException
from common.utils.logging_handler import Logger
from services import langchain_service
from services.agents.agent_prompts import (PREFIX, ROUTING_PREFIX,
                                           TASK_PREFIX, PLANNING_PREFIX,
                                           PLAN_FORMAT_INSTRUCTIONS,
                                           ROUTING_FORMAT_INSTRUCTIONS)
from services.agents.agent_tools import agent_tool_registry

Logger = Logger.get_logger(__file__)

class BaseAgent(ABC):
  """
  Base Class for LLM Service agents.  All agents are based on Langchain
  agents and basically specify the configuration for a particular variant
  of Langchain agent.
  """

  llm_type: str = None
  """ the LLM Service llm type used to power the agent """

  agent: LangchainAgent = None
  """ the langchain agent instance """

  agent_class: Type[LangchainAgent] = None
  """ the langchain agent class """

  name:str = None
  """ The name of the agent """

  prefix: str = PREFIX
  """ The prefix prompt of the agent """

  config: dict = {}
  """ Agent config dict from config file """

  def __init__(self, llm_type: str, name: str):
    self.llm_type = llm_type
    self.name = name
    self.agent = None
    self.config = get_agent_config()[self.name]

  def set_prefix(self, prefix) -> str:
    self.prefix = prefix


  @property
  def format_instructions(self) -> str:
    return FORMAT_INSTRUCTIONS

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    raise NotImplementedError(
        "Derived classes should provide output_parser_class")

  @classmethod
  @abstractmethod
  def capabilities(cls) -> List[str]:
    """ return capabilities of this agent class """

  def get_tools(self) -> List[Callable]:
    """ 
    Return tools used by this agent. The base method reads tools from
    agent config.  It supports special config like "ALL", specifying
    that the agent uses all tools.
    """
    agent_tools = []
    agent_config = get_agent_config()[self.name]
    tool_config = agent_config.get("tools", "")
    if tool_config == "ALL":
      agent_tools = list(agent_tool_registry.values())
    else:
      tool_config_list = get_config_list(tool_config)
      agent_tools = [tool for tool_name, tool in agent_tool_registry.items()
                     if tool_name in tool_config_list]
    return agent_tools

  @classmethod
  def load_llm_service_agent(cls, agent_name: str):
    agent_config = get_agent_config()[agent_name]
    llm_service_agent = agent_config["agent_class"](
        agent_config["llm_type"],
        agent_name
        )
    return llm_service_agent

  def load_langchain_agent(self,
                           input_variables: Optional[List[str]]=None) -> \
                           LangchainAgent:
    """ load this agent and return an instance of langchain Agent"""
    tools = self.get_tools()

    llm = langchain_service.get_model(self.llm_type)
    if llm is None:
      raise RuntimeError(
          f"Agent: cannot find LLM type {self.llm_type}")

    output_parser = self.output_parser_class()
    self.agent = self.agent_class.from_llm_and_tools(
        llm=llm,
        tools=tools,
        prefix=self.prefix,
        format_instructions=self.format_instructions,
        output_parser=output_parser,
        input_variables=input_variables
    )
    Logger.info(f"Successfully loaded {self.name} agent.")
    Logger.debug(f"prefix=[{self.prefix}], "
                 f"format_instructions=[{self.format_instructions}]",
                 f"input_variables=[{input_variables}]")
    return self.agent

  @classmethod
  def get_query_engines(cls, agent_name: str) -> \
      List[QueryEngine]:
    """ 
    Get list of query engines available to this agent.  Agent
    query engines can be configured in agent config, or tagged
    in query engine data models.
    """
    agent_config = get_agent_config()[agent_name]
    agent_query_engines = []

    if "query_engines" in agent_config:
      agent_qe_names = get_config_list(agent_config["query_engines"])
      if "ALL" in agent_qe_names:
        agent_query_engines = QueryEngine.fetch_all()
      else:
        agent_query_engines = QueryEngine.collection.filter(
          "name", "in", agent_qe_names).fetch()

    tagged_query_engines = QueryEngine.collection.filter(
        agent_name, "in", "agents"
    ).fetch()
    tagged_query_engines = tagged_query_engines or []

    query_engines = agent_query_engines + tagged_query_engines
    return query_engines

  @classmethod
  def get_datasets(cls, agent_name: str) -> dict:
    """
    Agent datasets are configured in agent config
    """
    agent_config = get_agent_config()[agent_name]
    agent_datasets = {}
    agent_dataset_names = []
    if "datasets" in agent_config:
      agent_dataset_names = get_config_list(agent_config["datasets"])
    datasets = get_dataset_config()
    agent_datasets = {
      ds_name: ds_config for ds_name, ds_config in datasets.items()
      if ds_name in agent_dataset_names
    }
    return agent_datasets

  @classmethod
  def get_llm_type_for_agent(cls, agent_name: str) -> str:
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

  @classmethod
  def get_agents_by_capability(cls, capability: str) -> List[str]:
    """
    Return config dicts for agents that support a specified capability
    """
    agent_config = get_agent_config()
    agent_capability_config = {}
    for agent_name, agent_config in agent_config.items():
      agent_class = agent_config.get("agent_class", None)
      if agent_class is None:
        raise RuntimeError(f"agent class not set for agent {agent_name}")
      capabilities = [ac.value for ac in agent_class.capabilities()]
      if capability in capabilities:
        agent_capability_config.update({agent_name: agent_config})
    return agent_capability_config


class ChatAgent(BaseAgent):
  """
  Chat Agent.  This is an agent configured for basic informational chat with a
  human.  It includes search and query tools.
  """
  def __init__(self, llm_type: str, name: str):
    super().__init__(llm_type, name)
    self.agent_class = ConversationalAgent

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    return ToolAgentOutputParser

  @classmethod
  def capabilities(cls) -> List[str]:
    """ return capabilities of this agent class """
    capabilities = [AgentCapability.AGENT_CHAT_CAPABILITY,
                    AgentCapability.AGENT_QUERY_CAPABILITY]
    return capabilities


class RoutingAgent(BaseAgent):
  """
  Routing Agent.  This is an agent configured for dispatching
  a given prompt to the best route with given list of choices.
  """
  def __init__(self, llm_type: str, name: str):
    super().__init__(llm_type, name)
    self.agent_class = ConversationalAgent
    self.prefix = ROUTING_PREFIX

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    return RoutingAgentOutputParser

  @property
  def format_instructions(self) -> str:
    return ROUTING_FORMAT_INSTRUCTIONS

  @classmethod
  def capabilities(cls) -> List[str]:
    """ return capabilities of this agent class """
    capabilities = [AgentCapability.AGENT_CHAT_CAPABILITY,
                    AgentCapability.AGENT_QUERY_CAPABILITY,
                    AgentCapability.AGENT_PLAN_CAPABILITY,
                    AgentCapability.AGENT_ROUTE_CAPABILITY]
    return capabilities


class TaskAgent(BaseAgent):
  """
  Structured Task Agent.  This agent accepts multiple inputs and can call
  StructuredTools that accept multiple inputs,not just one String. This is an
  agent configured to execute tasks on behalf of a human.  Every task has a
  plan, consisting of plan steps. Creation of the plan is done by a planning
  agent.
  """

  def __init__(self, llm_type: str, name: str):
    super().__init__(llm_type, name)
    self.agent_class = StructuredChatAgent

  @property
  def prefix(self) -> str:
    return TASK_PREFIX

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    return StructuredChatOutputParserWithRetries

  @property
  def format_instructions(self) -> str:
    return STRUCTURED_FORMAT_INSTRUCTIONS
  @classmethod
  def capabilities(cls) -> List[str]:
    """ return capabilities of this agent class """
    capabilities = [AgentCapability.AGENT_CHAT_CAPABILITY,
                    AgentCapability.AGENT_QUERY_CAPABILITY,
                    AgentCapability.AGENT_TASK_CAPABILITY]
    return capabilities

  def get_planning_agent(self) -> str:
    """
    This is the agent used by this agent to create plans for tasks.
    """
    return "PlanAgent"


class PlanAgent(BaseAgent):
  """
  Plan Agent.  This is an agent configured to make plans.
  Plans will be executed using a different agent.
  """

  def __init__(self, llm_type: str, name: str):
    super().__init__(llm_type, name)
    self.agent_class = StructuredChatAgent
    self.prefix = PLANNING_PREFIX

  @property
  def format_instructions(self) -> str:
    return PLAN_FORMAT_INSTRUCTIONS

  @property
  def output_parser_class(self) -> Type[AgentOutputParser]:
    return PlanAgentOutputParser

  @classmethod
  def capabilities(cls) -> List[str]:
    """ return capabilities of this agent class """
    capabilities = [AgentCapability.AGENT_PLAN_CAPABILITY]
    return capabilities


class RoutingAgentOutputParser(AgentOutputParser):
  """Output parser for a agent that makes plans."""

  ai_prefix: str = "AI"
  """Prefix to use before AI output."""

  def get_format_instructions(self) -> str:
    return ROUTING_FORMAT_INSTRUCTIONS

  def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
    regex = r"Action: (.*?)[\n]*Action Input: (.*)"
    match = re.search(regex, text)
    if not match:
      # TODO: undo this temporary fix to make the v1 agent terminate
      #raise OutputParserException(
      #    f"MIRA: Could not parse LLM output: `{text}`")
      return AgentFinish(
          {
            "output": text.split(f"{self.ai_prefix}:")[-1].strip()
          }, text
      )
    action = match.group(1)
    action_input = match.group(2)
    return AgentAction(action.strip(),
                       action_input.strip(" ").strip('"'), text)

  @property
  def _type(self) -> str:
    return "zero_shot"


class PlanAgentOutputParser(AgentOutputParser):
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
    print(f"[ToolAgentOutputParser] text: {text}")
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

