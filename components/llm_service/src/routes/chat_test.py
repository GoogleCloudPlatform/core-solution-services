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
  Unit tests for LLM Service endpoints
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock
from testing.test_config import API_URL, TESTING_FOLDER_PATH
from schemas.schema_examples import (LLM_GENERATE_EXAMPLE, CHAT_EXAMPLE,
                                     USER_EXAMPLE)
from common.models import UserChat, User
from common.models.llm import CHAT_HUMAN, CHAT_AI
from common.utils.http_exceptions import add_exception_handlers
from common.utils.auth_service import validate_user
from common.utils.auth_service import validate_token
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

with mock.patch("common.utils.secrets.get_secret"):
  with mock.patch("langchain.chat_models.ChatOpenAI", new=mock.AsyncMock()):
    with mock.patch("langchain.llms.Cohere", new=mock.AsyncMock()):
      from config import get_model_config

# assigning url
api_url = f"{API_URL}/chat"

with mock.patch("common.utils.secrets.get_secret"):
  from routes.chat import router

app = FastAPI()
add_exception_handlers(app)
app.include_router(router, prefix="/llm-service/api/v1")

FAKE_USER_DATA = {
    "id": "fake-user-id",
    "user_id": "fake-user-id",
    "auth_id": "fake-user-id",
    "email": "user@gmail.com",
    "role": "Admin"
}

FAKE_GENERATE_PARAMS = {
    "prompt": "test prompt",
    "llm_type": "VertexAI-Chat",
  }

FAKE_GENERATE_RESPONSE = "test generation"


@pytest.fixture
def client_with_emulator(clean_firestore, scope="module"):
  """ Create FastAPI test client with clean firestore emulator """
  def mock_validate_user():
    return True

  def mock_validate_token():
    return FAKE_USER_DATA

  app.dependency_overrides[validate_user] = mock_validate_user
  app.dependency_overrides[validate_token] = mock_validate_token
  test_client = TestClient(app)
  yield test_client


@pytest.fixture
def create_user(client_with_emulator):
  user_dict = USER_EXAMPLE
  user = User.from_dict(user_dict)
  user.save()


@pytest.fixture
def create_chat(client_with_emulator):
  chat_dict = CHAT_EXAMPLE
  chat = UserChat.from_dict(chat_dict)
  chat.save()


def test_get_chats(create_user, create_chat, client_with_emulator):
  params = {"skip": 0, "limit": "30"}
  url = f"{api_url}"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()

  assert resp.status_code == 200, "Status 200"
  saved_ids = [i.get("id") for i in json_response.get("data")]
  assert CHAT_EXAMPLE["id"] in saved_ids, "all data not retrieved"


def test_get_chat(create_user, create_chat, client_with_emulator):
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}"

  resp = client_with_emulator.get(url)
  json_response = resp.json()

  assert resp.status_code == 200, "Status 200"
  saved_id = json_response.get("data").get("id")
  assert chatid == saved_id, "all data not retrieved"


def test_create_chat(create_user, client_with_emulator):
  userid = CHAT_EXAMPLE["user_id"]
  url = f"{api_url}"

  # Test regular chat creation
  with mock.patch("routes.chat.llm_chat",
                  return_value=FAKE_GENERATE_RESPONSE):
    resp = client_with_emulator.post(url, data=FAKE_GENERATE_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")
  assert chat_data["history"][0] == \
    {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}, \
    "returned chat data prompt"
  assert chat_data["history"][1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "returned chat data generated text"

  # Test streaming chat creation
  streaming_params = {
    **FAKE_GENERATE_PARAMS,
    "stream": True
  }
  with mock.patch("routes.chat.llm_chat",
                  return_value=iter([FAKE_GENERATE_RESPONSE])):
    resp = client_with_emulator.post(url, data=streaming_params)
    assert resp.status_code == 200, "Streaming response status 200"
    assert resp.headers["content-type"] == "text/event-stream; charset=utf-8", \
      "Streaming response content type"

  # Test chat creation with history
  history_params = {
    **FAKE_GENERATE_PARAMS,
    "history": '[{"human": "test prompt"}, {"ai": "test response"}]'
  }
  with mock.patch("routes.chat.llm_chat",
                  return_value=FAKE_GENERATE_RESPONSE):
    resp = client_with_emulator.post(url, data=history_params)
  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")
  assert len(chat_data["history"]) == 2, "History preserved"
  assert chat_data["history"][0] == {"human": "test prompt"}, \
    "History human message preserved"
  assert chat_data["history"][1] == {"ai": "test response"}, \
    "History AI message preserved"

  # Test invalid history format
  invalid_history_params = {
    **FAKE_GENERATE_PARAMS,
    "history": 'invalid json'
  }
  resp = client_with_emulator.post(url, data=invalid_history_params)
  assert resp.status_code == 400, "Invalid history returns 400"

  # Test missing prompt and history
  invalid_params = {
    "llm_type": FAKE_GENERATE_PARAMS["llm_type"]
  }
  resp = client_with_emulator.post(url, data=invalid_params)
  assert resp.status_code == 400, "Missing prompt and history returns 400"

  # Verify final state
  user_chats = UserChat.find_by_user(userid)
  assert len(user_chats) == 3, "Created expected number of chats"

  # Verify the regular chat creation
  regular_chat = next(chat for chat in user_chats 
                     if len(chat.history) == 2 and 
                     chat.history[0].get(CHAT_HUMAN) == FAKE_GENERATE_PARAMS["prompt"])
  assert regular_chat.history[0] == \
    {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}, \
    "saved chat data prompt"
  assert regular_chat.history[1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "saved chat data generated text"


def test_delete_chat(create_user, create_chat, client_with_emulator):
  userid = CHAT_EXAMPLE["user_id"]
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}"

  resp = client_with_emulator.delete(url)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"

  user_chats = UserChat.find_by_user(userid)
  assert len(user_chats) == 0, "user chat deleted"


def test_update_chat(create_user, create_chat, client_with_emulator):
  userid = CHAT_EXAMPLE["user_id"]
  chatid = CHAT_EXAMPLE["id"]

  url = f"{api_url}/{chatid}"

  update_params = {
    "title": "updated title"
  }
  resp = client_with_emulator.put(url, json=update_params)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"

  updated_chat = UserChat.find_by_id(chatid)
  assert updated_chat.title == "updated title", "user chat updated"


def test_chat_generate(create_chat, client_with_emulator):
  chatid = CHAT_EXAMPLE["id"]

  url = f"{api_url}/{chatid}/generate"

  with mock.patch("routes.chat.llm_chat",
                  return_value=FAKE_GENERATE_RESPONSE):
    resp = client_with_emulator.post(url, json=FAKE_GENERATE_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")
  assert chat_data["history"][0] == CHAT_EXAMPLE["history"][0], \
    "returned chat history 0"
  assert chat_data["history"][1] == CHAT_EXAMPLE["history"][1], \
    "returned chat history 1"
  assert chat_data["history"][-2] == \
    {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}, \
    "returned chat data prompt"
  assert chat_data["history"][-1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "returned chat data generated text"

  user_chat = UserChat.find_by_id(chatid)
  assert user_chat is not None, "retrieved user chat"
  assert len(user_chat.history) == len(CHAT_EXAMPLE["history"]) + 2, \
    "user chat history updated"
  assert user_chat.history[-2] == \
    {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}, \
    "retrieved user chat prompt"
  assert user_chat.history[-1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "retrieved user chat response"

