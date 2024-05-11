# Copyright 2024 Google LLC
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

"""
  Unit tests for agent service
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,ungrouped-imports,wrong-import-position

from copy import deepcopy
import os
import json
import pytest
import tempfile
from unittest import mock
from common.models import User, UserChat
from common.models.agent import AgentCapability
from common.utils.logging_handler import Logger
from config import get_model_config, PROVIDER_LANGCHAIN
from testing.test_config import (TEST_OPENAI_CONFIG, FakeModelClass,
                                 FAKE_LANGCHAIN_GENERATION)
from schemas.schema_examples import (CHAT_EXAMPLE,
                                     USER_EXAMPLE)
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from services.agents.agent_service import run_agent

Logger = Logger.get_logger(__file__)

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

FAKE_AGENT_LOGS = "fake logs"
FAKE_AGENT_OUTPUT = "fake agent output"
DB_AGENT = "DbAgent"
CHAT_AGENT = "Chat"

FAKE_DB_AGENT_RESULT = {
  "data": {
    "columns": ["column-a", "column-b"],
    "rows": [
      ["fake-a1", "fake-b1"],
      ["fake-a2", "fake-b2"],
    ],
  },
  "resources": {"Spreadsheet": "https://example.com"}
}


@pytest.fixture
def create_user(firestore_emulator, clean_firestore):
  user_dict = USER_EXAMPLE
  user = User.from_dict(user_dict)
  user.save()
  return user

@pytest.fixture
def create_chat(firestore_emulator, clean_firestore):
  chat_dict = CHAT_EXAMPLE
  chat = UserChat.from_dict(chat_dict)
  chat.save()
  return chat

@pytest.fixture
def test_model_config(firestore_emulator, clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_OPENAI_CONFIG
  }
  get_model_config().llm_models = TEST_OPENAI_CONFIG


class FakeAgentExecutor():
  async def arun(self, prompt):
    return FAKE_AGENT_OUTPUT

class FakeLangchainAgent():
  pass

class FakeAgent():
  """ Fake agent class """
  def __init__(self):
    self.name = CHAT_AGENT
  def get_tools(self):
    return []
  def load_langchain_agent(self):
    return FakeLangchainAgent()
  def capabilities(self):
    return [AgentCapability.CHAT]


@pytest.mark.asyncio
@mock.patch("services.agents.agent_service.run_db_agent")
async def test_run_db_agent(mock_run_db_agent,
                            create_user, create_chat,
                            test_model_config):
  """ Test run_agent for db agent """
  mock_run_db_agent.return_value = FAKE_DB_AGENT_RESULT, FAKE_AGENT_LOGS

  agent_name = DB_AGENT
  prompt = "give me a list of chicken suppliers"
  agent_params = {
    "dataset": "fake-dataset",
    "user_email": create_user.email
  }

  chat_history = create_chat.history
  output = await run_agent(agent_name, prompt, chat_history, agent_params)

  assert output == FAKE_DB_AGENT_RESULT


@pytest.mark.asyncio
@mock.patch("services.agents.routing_agent.agent_executor_arun_with_logs")
@mock.patch("services.agents.routing_agent.AgentExecutor.from_agent_and_tools")
@mock.patch("services.agents.routing_agent.BaseAgent.get_llm_service_agent")
async def test_run_chat_agent(mock_get_agent,
                              mock_agent_executor,
                              mock_agent_executor_arun,
                              create_user, create_chat,
                              test_model_config):
  """ Test run_agent for chat agent """
  mock_get_agent.return_value = FakeAgent()
  mock_agent_executor.return_value = FakeAgentExecutor()
  mock_agent_executor_arun.return_value = FAKE_AGENT_OUTPUT, FAKE_AGENT_LOGS

  agent_name = CHAT_AGENT
  prompt = "how do you handle a broody chicken?"
  agent_params = None

  chat_history = create_chat.history
  output = await run_agent(agent_name, prompt, chat_history, agent_params)

  assert output == FAKE_AGENT_OUTPUT

