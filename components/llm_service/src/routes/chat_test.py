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
import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock
from testing.test_config import API_URL, TESTING_FOLDER_PATH
from schemas.schema_examples import (LLM_GENERATE_EXAMPLE, CHAT_EXAMPLE,
                                     USER_EXAMPLE)
from common.models import UserChat, User
from common.models.llm import CHAT_HUMAN, CHAT_AI, CHAT_FILE, CHAT_FILE_BASE64
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


@pytest.mark.asyncio
async def test_create_chat(create_user, client_with_emulator):
  """Test creating a new chat"""
  url = f"{api_url}"

  # Test regular chat creation
  with mock.patch("routes.chat.llm_chat",
                 return_value=FAKE_GENERATE_RESPONSE), \
       mock.patch("routes.chat.generate_chat_summary",
                 return_value="Test Summary"):
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
  assert chat_data["title"] == "Test Summary", \
    "chat title set from summary"

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
  with mock.patch("routes.chat.generate_chat_summary",
                 return_value="Test Summary"):
    resp = client_with_emulator.post(url, data=history_params)
  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")
  assert len(chat_data["history"]) == 2, "History preserved"
  assert chat_data["history"][0] == {"human": "test prompt"}, \
    "History human message preserved"
  assert chat_data["history"][1] == {"ai": "test response"}, \
    "History AI message preserved"
  assert chat_data["title"] == "Test Summary", \
    "chat title set from summary"

  # Test invalid history format
  invalid_history_params = {
    **FAKE_GENERATE_PARAMS,
    "history": "invalid json"
  }
  resp = client_with_emulator.post(url, data=invalid_history_params)
  assert resp.status_code == 422, "Invalid history returns 422"

  # Test missing prompt and history
  invalid_params = {
    "llm_type": FAKE_GENERATE_PARAMS["llm_type"]
  }
  # Don't mock llm_chat here since we expect validation to fail before reaching it
  resp = client_with_emulator.post(url, data=invalid_params)
  assert resp.status_code == 422, "Missing prompt and history returns 422"
  json_response = resp.json()
  assert json_response["success"] is False, "Error response indicates failure"
  assert "prompt" in json_response["message"].lower(), "Error message mentions missing prompt"
  assert json_response["data"] is None, "Error response has no data"

  # Verify final state
  user_chats = UserChat.find_by_user(USER_EXAMPLE["user_id"])
  assert len(user_chats) == 2, "Created expected number of chats"

  # Verify the regular chat creation
  regular_chat = next(chat for chat in user_chats
                     if len(chat.history) == 2 and
                     chat.history[0].get(CHAT_HUMAN) == \
                     FAKE_GENERATE_PARAMS["prompt"])
  assert regular_chat.history[0] == \
    {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}, \
    "saved chat data prompt"
  assert regular_chat.history[1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "saved chat data generated text"
  assert regular_chat.title == "Test Summary", \
    "chat title saved from summary"


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

  # Test updating title
  update_params = {
    "title": "updated title"
  }
  resp = client_with_emulator.put(url, json=update_params)
  assert resp.status_code == 200, "Status 200"
  updated_chat = UserChat.find_by_id(chatid)
  assert updated_chat.title == "updated title", "user chat title updated"

  # Test updating history
  new_history = [
    {"human": "new question"},
    {"ai": "new response"}
  ]
  update_params = {
    "history": new_history
  }
  resp = client_with_emulator.put(url, json=update_params)
  assert resp.status_code == 200, "Status 200"
  updated_chat = UserChat.find_by_id(chatid)
  assert updated_chat.history == new_history, "user chat history updated"

  # Test updating both title and history
  update_params = {
    "title": "another title",
    "history": [{"human": "q"}, {"ai": "a"}]
  }
  resp = client_with_emulator.put(url, json=update_params)
  assert resp.status_code == 200, "Status 200"
  updated_chat = UserChat.find_by_id(chatid)
  assert updated_chat.title == "another title", "title updated"
  assert updated_chat.history == \
      [{"human": "q"}, {"ai": "a"}], "history updated"


def test_chat_generate(create_user, create_chat, client_with_emulator):
  """Test generating a response in an existing chat"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"

  # Test regular generation
  with mock.patch("routes.chat.llm_chat",
                 return_value=FAKE_GENERATE_RESPONSE):
    resp = client_with_emulator.post(url, json=FAKE_GENERATE_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")
  assert chat_data["history"][-2] == \
    {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}, \
    "returned chat data prompt"
  assert chat_data["history"][-1] == \
    {CHAT_AI: FAKE_GENERATE_RESPONSE}, \
    "returned chat data generated text"

  # Test streaming generation
  streaming_params = {**FAKE_GENERATE_PARAMS, "stream": True}
  with mock.patch("routes.chat.llm_chat",
                 return_value=iter([FAKE_GENERATE_RESPONSE])):
    resp = client_with_emulator.post(url, json=streaming_params)
    assert resp.status_code == 200, "Streaming response status 200"
    assert resp.headers["content-type"] == "text/event-stream; charset=utf-8", \
      "Streaming response content type"

  # Test missing title generates summary
  chat = UserChat.find_by_id(chatid)
  chat.title = ""
  chat.save()

  with mock.patch("routes.chat.llm_chat",
                 return_value=FAKE_GENERATE_RESPONSE), \
       mock.patch("routes.chat.generate_chat_summary",
                 return_value="Test Summary"):
    resp = client_with_emulator.post(url, json=FAKE_GENERATE_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")
  assert chat_data["title"] == "Test Summary", \
    "Missing title generated summary"

  # Test existing title preserved
  chat = UserChat.find_by_id(chatid)
  chat.title = "Existing Title"
  chat.save()

  with mock.patch("routes.chat.llm_chat",
                 return_value=FAKE_GENERATE_RESPONSE), \
       mock.patch("routes.chat.generate_chat_summary") as mock_summary:
    resp = client_with_emulator.post(url, json=FAKE_GENERATE_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")
  assert chat_data["title"] == "Existing Title", \
    "Existing title preserved"
  mock_summary.assert_not_called(), \
    "Summary not generated for existing title"

def test_invalid_tool_names_chat(client_with_emulator):
  """Verify that llm tool name validation catches invalid cases"""
  url = f"{api_url}"
  create_generate_params = FAKE_GENERATE_PARAMS.copy()
  # testing with a non-list input string
  create_generate_params["tool_names"] = "(invalid_tool)"
  resp = client_with_emulator.post(url, data=create_generate_params)
  assert resp.status_code == 422
  json_response = resp.json()
  assert "json formatted list" in json_response["message"], json_response
  # testing with a tool that does not exist
  create_generate_params["tool_names"] = json.dumps(
    ["nonexistent_tool", "tool2"])
  resp = client_with_emulator.post(url, data=create_generate_params)
  assert resp.status_code == 422
  json_response = resp.json()
  assert "nonexistent_tool" in json_response["message"], json_response

def test_invalid_tool_names_chat_generate(create_user, create_chat,
                                          client_with_emulator):
  """Verify that llm tool name validation catches invalid cases"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"
  generate_params = FAKE_GENERATE_PARAMS.copy()
  # testing with a non-list input string
  generate_params["tool_names"] = "(invalid_tool,)"
  resp = client_with_emulator.post(url, json=generate_params)
  assert resp.status_code == 422

  json_response = resp.json()
  assert "json formatted list" in json_response["message"], json_response
  # testing with a tool that does not exist
  generate_params["tool_names"] = json.dumps(
    ["nonexistent_tool", "tool2"])
  resp = client_with_emulator.post(url, json=generate_params)
  assert resp.status_code == 422

  json_response = resp.json()
  assert "nonexistent_tool" in json_response["message"], json_response

@pytest.mark.long
def test_create_chat_code_interpreter(create_user, create_chat,
                                      client_with_emulator):
  url = f"{api_url}"
  generate_params = FAKE_GENERATE_PARAMS.copy()
  # testing with a non-list input strng
  generate_params["tool_names"] = '["vertex_code_interpreter_tool"]'
  generate_params["prompt"] = "give me a pie chart of continents by land area"
  resp = client_with_emulator.post(url, data=generate_params)
  assert resp.status_code == 200
  json_response = resp.json()
  user_chat = json_response["data"]
  assert len(user_chat["history"]) == 4, "user has unexpected number of entries"
  assert CHAT_FILE in user_chat["history"][2], "No generated file name found"
  assert CHAT_FILE_BASE64 in user_chat["history"][3], "File conetent not found"

@pytest.mark.long
def test_generate_chat_code_interpreter(create_user, create_chat,
                                      client_with_emulator):
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"
  generate_params = FAKE_GENERATE_PARAMS.copy()
  # testing with a non-list input strng
  generate_params["tool_names"] = '["vertex_code_interpreter_tool"]'
  generate_params["prompt"] = "give me a pie chart of continents by land area"
  resp = client_with_emulator.post(url, json=generate_params)
  assert resp.status_code == 200
  json_response = resp.json()
  user_chat = json_response["data"]
  assert len(user_chat["history"]) == len(CHAT_EXAMPLE["history"]) + 4
  assert CHAT_FILE in user_chat["history"][-2], "No generated file name found"
  assert CHAT_FILE_BASE64 in user_chat["history"][-1], "File conetent not found"

def test_generate_chat_summary(create_user, create_chat, client_with_emulator):
    """Test the generate_summary endpoint"""
    chatid = CHAT_EXAMPLE["id"]
    url = f"{api_url}/{chatid}/generate_summary"

    # Test successful summary generation
    with mock.patch(
            "services.llm_generate.generate_chat_summary",
            return_value="Test Summary"):
        resp = client_with_emulator.post(url)
        
        assert resp.status_code == 200
        json_response = resp.json()
        assert json_response["success"] is True
        assert json_response["data"]["title"] == "Test Summary"

        # Verify the chat was updated in the database
        updated_chat = UserChat.find_by_id(chatid)
        assert updated_chat.title == "Test Summary"

def test_generate_chat_summary_not_found(create_user, client_with_emulator):
    """Test generate_summary with non-existent chat"""
    url = f"{api_url}/non-existent-id/generate_summary"
    
    resp = client_with_emulator.post(url)
    assert resp.status_code == 404, "Non-existent chat returns 404"
    json_response = resp.json()
    assert json_response["success"] is False, "Error response indicates failure"
    assert "not found" in json_response["message"].lower(), "Error message indicates not found"
    assert json_response["data"] is None, "Error response has no data"

def test_generate_chat_summary_error(create_user, create_chat, client_with_emulator):
    """Test generate_summary when summary generation fails"""
    chatid = CHAT_EXAMPLE["id"]
    url = f"{api_url}/{chatid}/generate_summary"

    with mock.patch(
            "services.llm_generate.generate_chat_summary",
            side_effect=Exception("Summary generation failed")):
        resp = client_with_emulator.post(url)
        
        assert resp.status_code == 500, "Failed summary generation returns 500"
        json_response = resp.json()
        assert json_response["success"] is False, "Error response indicates failure"
        assert "summary generation failed" in json_response["message"].lower(), "Error message describes failure"
        assert json_response["data"] is None, "Error response has no data"

def test_create_chat_generates_summary(create_user, client_with_emulator):
    """Test that creating a new chat generates a summary"""
    url = f"{api_url}"

    # Test regular chat creation with summary generation
    with mock.patch("routes.chat.llm_chat",
                   return_value=FAKE_GENERATE_RESPONSE), \
         mock.patch("services.llm_generate.generate_chat_summary",
                   return_value="Test Summary"):
        
        resp = client_with_emulator.post(url, data=FAKE_GENERATE_PARAMS)

        json_response = resp.json()
        assert resp.status_code == 200
        chat_data = json_response.get("data")
        
        # Verify chat was created with correct content
        assert chat_data["history"][0] == \
            {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}
        assert chat_data["history"][1] == \
            {CHAT_AI: FAKE_GENERATE_RESPONSE}
        
        # Verify summary was generated and set as title
        assert chat_data["title"] == "Test Summary"

        # Verify chat was saved to database with summary
        chat = UserChat.find_by_id(chat_data["id"])
        assert chat.title == "Test Summary"

def test_create_chat_with_history_generates_summary(create_user, client_with_emulator):
    """Test that creating a chat from history generates a summary"""
    url = f"{api_url}"
    
    history_params = {
        **FAKE_GENERATE_PARAMS,
        "history": '[{"human": "test prompt"}, {"ai": "test response"}]'
    }

    with mock.patch("services.llm_generate.generate_chat_summary",
                   return_value="Test Summary"):
        resp = client_with_emulator.post(url, data=history_params)
        
        json_response = resp.json()
        assert resp.status_code == 200
        chat_data = json_response.get("data")
        
        # Verify history was preserved
        assert len(chat_data["history"]) == 2
        assert chat_data["history"][0] == {"human": "test prompt"}
        assert chat_data["history"][1] == {"ai": "test response"}
        
        # Verify summary was generated and set as title
        assert chat_data["title"] == "Test Summary"

        # Verify chat was saved to database with summary
        chat = UserChat.find_by_id(chat_data["id"])
        assert chat.title == "Test Summary"

def test_chat_generate_adds_missing_title(create_user, create_chat, client_with_emulator):
  """Test that generating a chat response adds a title if missing"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"

  # First remove the title
  chat = UserChat.find_by_id(chatid)
  chat.title = ""
  chat.save()

  with mock.patch("routes.chat.llm_chat",
                 return_value=FAKE_GENERATE_RESPONSE), \
       mock.patch("services.llm_generate.generate_chat_summary",
                 return_value="Test Summary"):
    
    resp = client_with_emulator.post(url, json=FAKE_GENERATE_PARAMS)

    json_response = resp.json()
    assert resp.status_code == 200
    chat_data = json_response.get("data")
    
    # Verify chat response was generated
    assert chat_data["history"][-2] == \
        {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}
    assert chat_data["history"][-1] == \
        {CHAT_AI: FAKE_GENERATE_RESPONSE}
    
    # Verify summary was generated and set as title
    assert chat_data["title"] == "Test Summary"

    # Verify chat was saved to database with summary
    updated_chat = UserChat.find_by_id(chatid)
    assert updated_chat.title == "Test Summary"

def test_chat_generate_keeps_existing_title(create_user, create_chat, client_with_emulator):
  """Test that generating a chat response preserves existing title"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"

  # Set an existing title
  chat = UserChat.find_by_id(chatid)
  chat.title = "Existing Title"
  chat.save()

  with mock.patch("routes.chat.llm_chat",
                 return_value=FAKE_GENERATE_RESPONSE), \
       mock.patch("services.llm_generate.generate_chat_summary",
                 return_value="Test Summary") as mock_summary:
    
    resp = client_with_emulator.post(url, json=FAKE_GENERATE_PARAMS)

    json_response = resp.json()
    assert resp.status_code == 200
    chat_data = json_response.get("data")
    
    # Verify chat response was generated
    assert chat_data["history"][-2] == \
        {CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]}
    assert chat_data["history"][-1] == \
        {CHAT_AI: FAKE_GENERATE_RESPONSE}
    
    # Verify title was preserved and summary was not generated
    assert chat_data["title"] == "Existing Title"
    mock_summary.assert_not_called()

    # Verify chat in database still has original title
    updated_chat = UserChat.find_by_id(chatid)
    assert updated_chat.title == "Existing Title"
