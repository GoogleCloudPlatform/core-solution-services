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
from common.models import (User, UserChat, QueryResult,
                           QueryEngine, UserPlan, PlanStep)
from common.models.llm import CHAT_AI
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
FAKE_QUERY_ROUTE_NAME = f"Query Engine: {QUERY_ENGINE_EXAMPLE['name']}"
FAKE_PLAN_ROUTE = "Plan"
FAKE_DATASET = "fake-dataset"
FAKE_DATASET_DESCRIPTION = "fake dataset description"
FAKE_DB_ROUTE = f"Database:{FAKE_DATASET}"
FAKE_CHAT_ROUTE = "Chat"

FAKE_AGENT_LOGS = "fake logs"
FAKE_AGENT_OUTPUT = "fake agent output"
ROUTING_AGENT = "Routing"

FAKE_INTENT_OUTPUT = \
    f"Route:\n1. Use [Database:{FAKE_DATASET}] to query a database"

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


class FakeAgentExecutor():
  async def arun(self, prompt):
    return FAKE_INTENT_OUTPUT

class FakeLangchainAgent():
  pass

class FakeAgent():
  """ Fake agent class """
  def __init__(self, query_engines):
    self.name = ROUTING_AGENT
    self.query_engines = query_engines
    self.datasets = {FAKE_DATASET: {"description": FAKE_DATASET_DESCRIPTION}}
  def get_tools(self):
    return []
  def load_langchain_agent(self):
    return FakeLangchainAgent()
  def get_query_engines(self, agent_name):
    return self.query_engines
  def get_datasets(self, agent_name):
    return self.datasets


@pytest.mark.asyncio
@mock.patch("services.agents.routing_agent.query_generate")
@mock.patch("services.agents.routing_agent.run_intent")
async def test_query_route(mock_run_intent,
                           mock_query_generate,
                           test_model_config,
                           create_user, create_chat,
                           create_query_engine, create_query_result):
  """ Test run_routing_agent with query route """

  mock_run_intent.return_value = FAKE_QUERY_ROUTE, FAKE_AGENT_LOGS
  mock_query_generate.return_value = create_query_result, FAKE_REFERENCES

  agent_name = ROUTING_AGENT
  prompt = "when does a chicken start laying eggs?"

  route, response_data = await run_routing_agent(
      prompt, agent_name, create_user, create_chat)

  assert route == FAKE_QUERY_ROUTE
  assert response_data["route"] == AgentCapability.QUERY.value
  assert response_data["route_name"] == FAKE_QUERY_ROUTE_NAME
  assert response_data["output"] == create_query_result.response
  assert response_data["query_engine_id"] == create_query_engine.id
  assert response_data["query_references"] == FAKE_REFERENCES
  assert response_data["agent_logs"] == FAKE_AGENT_LOGS


@pytest.mark.asyncio
@mock.patch("services.agents.routing_agent.agent_plan")
@mock.patch("services.agents.routing_agent.run_intent")
async def test_plan_route(mock_run_intent,
                          mock_agent_plan,
                          test_model_config,
                          create_user, create_chat, create_plan):
  """ Test run_routing_agent with plan route """

  fake_plan_result = create_plan.get_fields(reformat_datetime=True)
  fake_plan_result["id"] = create_plan.id

  mock_run_intent.return_value = FAKE_PLAN_ROUTE, FAKE_AGENT_LOGS
  mock_agent_plan.return_value = FAKE_AGENT_OUTPUT, create_plan

  agent_name = ROUTING_AGENT
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
@mock.patch("services.agents.routing_agent.run_db_agent")
@mock.patch("services.agents.routing_agent.run_intent")
async def test_db_route(mock_run_intent,
                        mock_run_db_agent,
                        test_model_config,
                        create_user, create_chat):
  """ Test run_routing_agent with db route """

  mock_run_intent.return_value = FAKE_DB_ROUTE, FAKE_AGENT_LOGS
  mock_run_db_agent.return_value = FAKE_DB_AGENT_RESULT, FAKE_AGENT_LOGS

  agent_name = ROUTING_AGENT
  prompt = "who are the most popular chickens?"

  route, response_data = await run_routing_agent(
      prompt, agent_name, create_user, create_chat)

  assert route == FAKE_DB_ROUTE
  assert response_data["route"] == AgentCapability.DATABASE.value
  assert response_data["route_name"] == f"Database Query: {FAKE_DATASET}"
  assert response_data["content"]
  assert response_data["dataset"] == FAKE_DATASET
  assert response_data["agent_logs"] == FAKE_AGENT_LOGS
  assert response_data[CHAT_AI]
  assert response_data["resources"]


@pytest.mark.asyncio
@mock.patch("services.agents.routing_agent.run_agent")
@mock.patch("services.agents.routing_agent.run_intent")
async def test_chat_route(mock_run_intent,
                          mock_run_agent,
                          test_model_config,
                          create_user, create_chat):
  """ Test run_routing_agent with chat route """

  mock_run_intent.return_value = FAKE_CHAT_ROUTE, FAKE_AGENT_LOGS
  mock_run_agent.return_value = FAKE_AGENT_OUTPUT

  agent_name = ROUTING_AGENT
  prompt = "how can I raise the best chickens?"

  route, response_data = await run_routing_agent(
      prompt, agent_name, create_user, create_chat)

  assert route == AgentCapability.CHAT.value
  assert response_data["route"] == AgentCapability.CHAT.value
  assert response_data["route_name"] == AgentCapability.CHAT.value
  assert response_data["content"] == FAKE_AGENT_OUTPUT
  assert "agent_logs" not in response_data


@pytest.mark.asyncio
@mock.patch("services.agents.routing_agent.agent_executor_arun_with_logs")
@mock.patch("services.agents.routing_agent.AgentExecutor.from_agent_and_tools")
@mock.patch("services.agents.routing_agent.BaseAgent.get_llm_service_agent")
async def test_run_intent(mock_get_agent,
                          mock_agent_executor,
                          mock_agent_executor_arun,
                          test_model_config,
                          create_user, create_chat, create_query_engine):
  """ Test run_intent """

  mock_get_agent.return_value = FakeAgent([create_query_engine])
  mock_agent_executor.return_value = FakeAgentExecutor()
  mock_agent_executor_arun.return_value = FAKE_INTENT_OUTPUT, FAKE_AGENT_LOGS

  agent_name = ROUTING_AGENT
  prompt = "how can I raise the best chickens?"

  chat_history = create_chat.history
  route, route_logs = await run_intent(agent_name, prompt, chat_history)

  assert route == FAKE_DB_ROUTE
  assert route_logs == FAKE_AGENT_LOGS

