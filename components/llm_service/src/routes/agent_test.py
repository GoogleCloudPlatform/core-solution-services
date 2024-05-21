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

"""
  Unit tests for LLM Service agent endpoints
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock
from schemas.schema_examples import (LLM_GENERATE_EXAMPLE, CHAT_EXAMPLE,
                                     USER_EXAMPLE)
from common.models.llm import CHAT_HUMAN, CHAT_AI
from common.models import UserChat, User
from common.utils.http_exceptions import add_exception_handlers
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from common.utils.config import set_env_var

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

with set_env_var("PG_HOST", ""):
  from testing.test_config import API_URL, FakeAgentExecutor, FakeAgent


FAKE_AGENT_RUN_PARAMS = {
    "llm_type": "VertexAI-Chat",
    "prompt": "test prompt"
  }

FAKE_GENERATE_RESPONSE = "test generation"
FAKE_AGENT_LOGS = "fake agent thought process logs"

FAKE_AGENT_OUTPUT = "fake agent output"
FAKE_DATASET = "fake-dataset"

FAKE_DB_AGENT_RESULT = {
  "db_result": [
    {
      "column-a": "fake-a1",
      "column-b": "fake-b1"
    },
    {
      "column-a": "fake-a2",
      "column-b": "fake-b2"
    }
  ],
  "dataset": FAKE_DATASET,
  "resources": {"Spreadsheet": "https://example.com"},
  CHAT_AI: FAKE_AGENT_OUTPUT,
  "content": FAKE_AGENT_OUTPUT,
}


# assigning url
api_url = f"{API_URL}/agent"

with mock.patch("common.utils.secrets.get_secret"):
  from routes.agent import router
  from common.testing.client_with_emulator import client_with_emulator
  from services.agents.agent_service import get_all_agents

app = FastAPI()
add_exception_handlers(app)
app.include_router(router, prefix="/llm-service/api/v1")


@pytest.fixture
def create_user(clean_firestore):
  user_dict = USER_EXAMPLE
  user = User.from_dict(user_dict)
  user.save()

@pytest.fixture
def create_chat(clean_firestore):
  chat_dict = CHAT_EXAMPLE
  chat = UserChat.from_dict(chat_dict)
  chat.save()


def test_get_agent_list(clean_firestore, client_with_emulator):
  url = f"{api_url}"
  resp = client_with_emulator.get(url)
  json_response = resp.json()
  agent_config = get_all_agents()
  # cast all agent config into str
  for a, ac in agent_config.items():
    for k, v in ac.items():
      ac[k] = str(v)
  assert resp.status_code == 200, "Status 200"
  assert json_response.get("data") == agent_config


@pytest.mark.anyio
@mock.patch("services.agents.agent_service.agent_executor_arun_with_logs")
@mock.patch("services.agents.agent_service.AgentExecutor.from_agent_and_tools")
@mock.patch("services.agents.agent_service.BaseAgent.get_llm_service_agent")
def test_run_agent(mock_get_agent,
                   mock_agent_executor,
                   mock_agent_executor_arun,
                   create_user, client_with_emulator):
  """ Test run_agent """

  mock_get_agent.return_value = FakeAgent()
  mock_agent_executor.return_value = FakeAgentExecutor()
  mock_agent_executor_arun.return_value = FAKE_AGENT_OUTPUT, FAKE_AGENT_LOGS

  userid = CHAT_EXAMPLE["user_id"]
  url = f"{api_url}/run/Chat"
  resp = client_with_emulator.post(url, json=FAKE_AGENT_RUN_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  response_data = json_response.get("data")
  chat_data = response_data.get("chat")
  assert chat_data["history"][0] == \
    {CHAT_HUMAN: FAKE_AGENT_RUN_PARAMS["prompt"]}, \
    "returned chat data prompt"
  assert chat_data["history"][1] == \
    {CHAT_AI: FAKE_AGENT_OUTPUT}, \
    "returned chat data generated text"

  user_chats = UserChat.find_by_user(userid)
  assert len(user_chats) == 1, "retrieved new user chat"
  user_chat = user_chats[0]
  assert user_chat.history[0] == \
    {CHAT_HUMAN: FAKE_AGENT_RUN_PARAMS["prompt"]}, \
    "retrieved user chat prompt"
  assert user_chat.history[1] == \
    {CHAT_AI: FAKE_AGENT_OUTPUT}, \
    "retrieved user chat response"

@pytest.mark.anyio
def test_run_agent_chat(create_user, create_chat, client_with_emulator):
  """ Test run_agent with chat agent """
  chatid = CHAT_EXAMPLE["id"]

  url = f"{api_url}/run/Chat/{chatid}"

  with mock.patch("routes.agent.run_agent",
                  return_value = (FAKE_GENERATE_RESPONSE, FAKE_AGENT_LOGS)):
    resp = client_with_emulator.post(url, json=FAKE_AGENT_RUN_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  response_data = json_response.get("data")
  chat_data = response_data.get("chat")
  assert chat_data["history"][0] == CHAT_EXAMPLE["history"][0], \
    "returned chat history 0"
  assert chat_data["history"][1] == CHAT_EXAMPLE["history"][1], \
    "returned chat history 1"
  assert chat_data["history"][-2] == \
    {CHAT_HUMAN: FAKE_AGENT_RUN_PARAMS["prompt"]}, \
    "returned chat data prompt"
  assert chat_data["history"][-1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "returned chat data generated text"

  user_chat = UserChat.find_by_id(chatid)
  assert user_chat is not None, "retrieved user chat"
  assert len(user_chat.history) == len(CHAT_EXAMPLE["history"]) + 2, \
    "user chat history updated"
  assert user_chat.history[-2] == \
    {CHAT_HUMAN: FAKE_AGENT_RUN_PARAMS["prompt"]}, \
    "retrieved user chat prompt"
  assert user_chat.history[-1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "retrieved user chat response"

@pytest.mark.anyio
@mock.patch("services.agents.agent_service.run_db_agent")
def test_run_agent_db(mock_run_db_agent, create_user, client_with_emulator):
  """ Test run_agent with db agent """
  mock_run_db_agent.return_value = FAKE_DB_AGENT_RESULT, FAKE_AGENT_LOGS

  url = f"{api_url}/run/DbAgent"
  resp = client_with_emulator.post(url, json=FAKE_AGENT_RUN_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  response_data = json_response.get("data")
