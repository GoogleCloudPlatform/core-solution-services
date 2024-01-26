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
  Unit tests for LLM Service routing agent
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports,wrong-import-position
import os
import json
import pytest
import tempfile
from unittest import mock
from common.models import User, UserChat, QueryResult
from common.models.agent import AgentCapability
from config import (get_model_config, PROVIDER_LANGCHAIN,
                    OPENAI_LLM_TYPE_GPT4,
                    VERTEX_LLM_TYPE_BISON_CHAT_LANGCHAIN,
                    OPENAI_LLM_TYPE_GPT4_LATEST)
from testing.test_config import TEST_OPENAI_CONFIG
from schemas.schema_examples import (CHAT_EXAMPLE, USER_EXAMPLE,
                                     QUERY_RESULT_EXAMPLE)
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from services.agents.routing_agent import run_intent, run_routing_agent

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

FAKE_QUERY_ROUTE = "Query"
FAKE_AGENT_LOGS = ""
FAKE_ROUTING_AGENT = "Router"

TEST_AGENT_CONFIG = {
  "Agents":
  {
    FAKE_ROUTING_AGENT: {
      "llm_type": OPENAI_LLM_TYPE_GPT4,
      "agent_type": "langchain_Conversational",
      "agent_class": "RoutingAgent",
      "tools": ""
    },
    "Chat": {
      "llm_type": VERTEX_LLM_TYPE_BISON_CHAT_LANGCHAIN,
      "agent_type": "langchain_Conversational",
      "agent_class": "ChatAgent",
      "tools": "search_tool,query_tool",
      "query_engines": "ALL"
    },
    "Task": {
      "llm_type": OPENAI_LLM_TYPE_GPT4_LATEST,
      "agent_type": "langchain_StructuredChatAgent",
      "agent_class": "TaskAgent",
      "tools": "ALL"
    },
    "Plan": {
      "llm_type": OPENAI_LLM_TYPE_GPT4_LATEST,
      "agent_type": "langchain_ZeroShot",
      "agent_class": "PlanAgent",
      "query_engines": "ALL",
      "tools": "ALL"
    }
  }
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
def create_query_result(firestore_emulator, clean_firestore):
  query_result_dict = QUERY_RESULT_EXAMPLE
  query_result = QueryResult.from_dict(query_result_dict)
  query_result.save()
  return query_result

@pytest.fixture
def test_model_config(firestore_emulator, clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_OPENAI_CONFIG
  }
  get_model_config().llm_models = TEST_OPENAI_CONFIG
  

class FakeAgentExecutor():
  async def arun(self, prompt):
    return ""

class FakeQueryTool():
  def run(self, statement):
    return ""

@pytest.mark.asyncio
@mock.patch("services.agents.routing_agent.run_intent")
@mock.patch("services.agents.routing_agent.query_generate")
@mock.patch("config.utils.get_agent_config")
async def test_query_route(mock_run_intent,
                           mock_query_generate,
                           mock_get_agent_config,
                           test_model_config,
                           create_user, create_chat, create_query_result):
  """ Test run_routing_agent with query route """

  mock_run_intent.return_value = FAKE_QUERY_ROUTE, FAKE_AGENT_LOGS
  mock_query_generate.return_value = create_query_result
  mock_get_agent_config.return_value = TEST_AGENT_CONFIG

  agent_name = FAKE_ROUTING_AGENT
  prompt = "when does a chicken start laying eggs?"
  route, response_data = await run_routing_agent(
      agent_name, prompt, create_user, create_chat)

  assert route == AgentCapability.AGENT_QUERY_CAPABILITY.value
  
  #assert response_data["resources"]["Spreadsheet"] == "test url"

