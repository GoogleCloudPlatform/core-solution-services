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
from config.utils import set_agent_config
from common.models import (User, UserChat, QueryResult,
                           QueryEngine, UserPlan, PlanStep)
from common.models.agent import AgentCapability
from common.utils.logging_handler import Logger
from config import (get_model_config, PROVIDER_LANGCHAIN,
                    OPENAI_LLM_TYPE_GPT4,
                    VERTEX_LLM_TYPE_BISON_CHAT_LANGCHAIN,
                    OPENAI_LLM_TYPE_GPT4_LATEST)
from testing.test_config import TEST_OPENAI_CONFIG
from schemas.schema_examples import (CHAT_EXAMPLE,
                                     USER_EXAMPLE,
                                     QUERY_RESULT_EXAMPLE,
                                     QUERY_ENGINE_EXAMPLE,
                                     USER_QUERY_EXAMPLE,
                                     USER_PLAN_EXAMPLE,
                                     USER_PLAN_STEPS_EXAMPLE_1,
                                     USER_PLAN_STEPS_EXAMPLE_2)
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from services.agents.routing_agent import run_intent, run_routing_agent

Logger = Logger.get_logger(__file__)

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

FAKE_QUERY_ROUTE = f"Query:{QUERY_ENGINE_EXAMPLE['name']}"
FAKE_PLAN_ROUTE = "Plan"
FAKE_DB_ROUTE = "Database"

FAKE_AGENT_LOGS = "fake logs"
FAKE_AGENT_OUTPUT = "fake agent output"
FAKE_ROUTING_AGENT = "Router"

FAKE_DB_AGENT_RESULT = {}

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

FAKE_REFERENCES = USER_QUERY_EXAMPLE["history"][1]["AIReferences"]


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
def create_query_engine(firestore_emulator, clean_firestore):
  query_engine_dict = QUERY_ENGINE_EXAMPLE
  q_engine = QueryEngine.from_dict(query_engine_dict)
  q_engine.save()
  return q_engine

@pytest.fixture
def create_plan(clean_firestore):
  plan_dict = USER_PLAN_EXAMPLE
  plan = UserPlan.from_dict(plan_dict)
  plan.save()
  plan_step = PlanStep.from_dict(USER_PLAN_STEPS_EXAMPLE_1)
  plan_step.save()
  plan_step = PlanStep.from_dict(USER_PLAN_STEPS_EXAMPLE_2)
  plan_step.save()
  return plan

@pytest.fixture
def test_model_config(firestore_emulator, clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_OPENAI_CONFIG
  }
  get_model_config().llm_models = TEST_OPENAI_CONFIG

@pytest.fixture
def test_agent_config(firestore_emulator, clean_firestore):
  set_agent_config(TEST_AGENT_CONFIG)

class FakeAgentExecutor():
  async def arun(self, prompt):
    return ""

class FakeQueryTool():
  def run(self, statement):
    return ""

@pytest.mark.asyncio
@mock.patch("config.utils.get_agent_config")
@mock.patch("services.agents.routing_agent.query_generate")
@mock.patch("services.agents.routing_agent.run_intent")
async def test_query_route(mock_run_intent,
                           mock_query_generate,
                           mock_get_agent_config,
                           test_model_config,
                           test_agent_config,
                           create_user, create_chat,
                           create_query_engine, create_query_result):
  """ Test run_routing_agent with query route """

  mock_run_intent.return_value = FAKE_QUERY_ROUTE, FAKE_AGENT_LOGS
  mock_query_generate.return_value = create_query_result, FAKE_REFERENCES
  mock_get_agent_config.return_value = TEST_AGENT_CONFIG

  agent_name = FAKE_ROUTING_AGENT
  prompt = "when does a chicken start laying eggs?"

  route, response_data = await run_routing_agent(
      prompt, agent_name, create_user, create_chat)

  assert route == FAKE_QUERY_ROUTE
  assert response_data["route"] == AgentCapability.QUERY.value
  assert response_data["route_name"] == FAKE_QUERY_ROUTE
  assert response_data["output"] == create_query_result.response
  assert response_data["query_engine_id"] == create_query_engine.id
  assert response_data["query_references"] == FAKE_REFERENCES
  assert response_data["agent_logs"] == FAKE_AGENT_LOGS


@pytest.mark.asyncio
@mock.patch("config.utils.get_agent_config")
@mock.patch("services.agents.routing_agent.agent_plan")
@mock.patch("services.agents.routing_agent.run_intent")
async def test_plan_route(mock_run_intent,
                          mock_agent_plan,
                          mock_get_agent_config,
                          test_model_config,
                          test_agent_config,
                          create_user, create_chat, create_plan):
  """ Test run_routing_agent with plan route """

  fake_plan_result = create_plan.get_fields(reformat_datetime=True)
  fake_plan_result["id"] = create_plan.id

  mock_run_intent.return_value = FAKE_PLAN_ROUTE, FAKE_AGENT_LOGS
  mock_agent_plan.return_value = FAKE_AGENT_OUTPUT, create_plan
  mock_get_agent_config.return_value = TEST_AGENT_CONFIG

  agent_name = FAKE_ROUTING_AGENT
  prompt = "make a plan to get some chickens"

  route, response_data = await run_routing_agent(
      prompt, agent_name, create_user, create_chat)

  assert route == AgentCapability.PLAN.value
  assert response_data["route"] == AgentCapability.PLAN.value
  assert response_data["route_name"] == FAKE_PLAN_ROUTE
  assert response_data["content"] == FAKE_AGENT_OUTPUT
  assert response_data["plan"] == fake_plan_result
  assert response_data["agent_logs"] == FAKE_AGENT_OUTPUT


@pytest.mark.asyncio
@mock.patch("config.utils.get_agent_config")
@mock.patch("services.agents.routing_agent.run_db_agent")
@mock.patch("services.agents.routing_agent.run_intent")
async def test_db_route(mock_run_intent,
                        mock_run_db_agent,
                        mock_get_agent_config,
                        test_model_config,
                        test_agent_config,
                        create_user, create_chat):
  """ Test run_routing_agent with db route """

  mock_run_intent.return_value = FAKE_DB_ROUTE, FAKE_AGENT_LOGS
  mock_run_db_agent.return_value = FAKE_DB_AGENT_RESULT
  mock_get_agent_config.return_value = TEST_AGENT_CONFIG

  agent_name = FAKE_ROUTING_AGENT
  prompt = "when does a chicken start laying eggs?"

  route, response_data = await run_routing_agent(
      prompt, agent_name, create_user, create_chat)

#
  #assert route == AgentCapability.QUERY.value

  #assert response_data["resources"]["Spreadsheet"] == "test url"

