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

from typing import Optional, Union, Any
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from config import (LANGCHAIN_LLM, GOOGLE_LLM, CHAT_LLM_TYPES)
from langchain.agents import (Agent, AgentOutputParser,
                              AgentExecutor, ConversationalAgent)
from langchain.schema import AgentAction, AgentFinish, OutputParserException
from langchain.chains import LLMChain
from services.agent_prompts import PREFIX
from services.agent_tools import medicaid_eligibility_requirements

class MediKateAgent:

  llm_type = None
  agent = None

  def __init__(self, llm_type: str):
    self.llm_type = llm_type

  def load_agent(self) -> Agent:
    """ load this agent and return an instance of langchain Agent"""
    tools = self.get_tools()

    llm = CHAT_LLM_TYPES.get(self.llm_type)
    if llm is None:
      raise InternalServerError(
          f"MediKateAgent: cannot find LLM type {self.llm_type}")

    output_parser = MediKateOutputParser()

    self.agent = ConversationalAgent.from_llm_and_tools(
        llm=llm,
        tools=tools,
        output_parser=output_parser,
        prefix=PREFIX
    )
    return agent

  def get_tools(self):
    tools = [medicaid_eligibility_requirements]
    return tools


class MediKateOutputParser(AgentOutputParser):

  def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
    # Check if agent should finish
    if "Final Answer:" in llm_output:
      return AgentFinish(
        # Return values is generally always a dictionary with a single `output` key
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
    return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)  
  