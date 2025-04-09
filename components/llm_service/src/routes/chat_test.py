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
# pylint: disable=unused-argument,redefined-outer-name,unused-import
# pylint: disable=unused-variable,ungrouped-imports
import os
import json
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock
from testing.test_config import API_URL, TESTING_FOLDER_PATH
from schemas.schema_examples import (LLM_GENERATE_EXAMPLE, CHAT_EXAMPLE,
                                     USER_EXAMPLE, QUERY_ENGINE_EXAMPLE)
from common.models import UserChat, User, QueryEngine, QueryReference
from common.models.llm import (CHAT_HUMAN, CHAT_AI, CHAT_FILE, CHAT_FILE_BASE64,
                             CHAT_SOURCE, CHAT_QUERY_RESULT,
                             CHAT_QUERY_REFERENCES)
from common.utils.http_exceptions import add_exception_handlers
from common.utils.auth_service import validate_user
from common.utils.auth_service import validate_token
from common.testing.firestore_emulator import (
  firestore_emulator, clean_firestore
)

from services.query.query_service import query_generate_for_chat
from services.query.data_source import DataSourceFile

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


@pytest.fixture
def create_engine(firestore_emulator, clean_firestore):
  """Create a test query engine"""
  query_engine_dict = QUERY_ENGINE_EXAMPLE
  q_engine = QueryEngine.from_dict(query_engine_dict)
  q_engine.save()
  return q_engine


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
  url = f"{api_url}/empty_chat"
  resp = client_with_emulator.post(url)
  assert resp.status_code == 200, "Failed to create empty chat"
  json_response = resp.json()
  chat_data = json_response["data"]
  assert "id" in chat_data, "Chat ID not found in generated chat"

def test_create_chat_deprecated(create_user, client_with_emulator):
  userid = CHAT_EXAMPLE["user_id"]
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
  # Skip mocking llm_chat since validation will fail before it would be called
  resp = client_with_emulator.post(url, data=invalid_params)
  assert resp.status_code == 422, "Missing prompt and history returns 422"
  json_response = resp.json()
  assert json_response["success"] is False, "Error response indicates failure"
  error_msg = "Error message mentions missing prompt"
  assert "prompt" in json_response["message"].lower(), error_msg
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
  assert not mock_summary.called, "Summary not generated for existing title"

def test_invalid_tool_names_chat(client_with_emulator):
  """Verify that llm tool name validation catches invalid cases"""
  url = f"{api_url}"
  create_generate_params = FAKE_GENERATE_PARAMS.copy()
  # testing with a non-list input string
  create_generate_params["tool_names"] = "(invalid_tool)"
  resp = client_with_emulator.post(url, data=create_generate_params)
  assert resp.status_code == 422
  json_response = resp.json()
  assert "detail" in json_response, str(json_response)
  assert "json formatted list" in json_response["detail"]
  # testing with a tool that does not exist
  create_generate_params["tool_names"] = json.dumps(
    ["nonexistent_tool", "tool2"])
  resp = client_with_emulator.post(url, data=create_generate_params)
  assert resp.status_code == 422
  json_response = resp.json()
  assert "nonexistent_tool" in json_response["detail"]

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
  assert "json formatted list" in json_response["detail"]
  # testing with a tool that does not exist
  generate_params["tool_names"] = json.dumps(
    ["nonexistent_tool", "tool2"])
  resp = client_with_emulator.post(url, json=generate_params)
  assert resp.status_code == 422
  json_response = resp.json()
  assert "nonexistent_tool" in json_response["detail"]


@pytest.mark.long
def test_generate_chat_code_interpreter(
    create_user,
    create_chat,
    client_with_emulator
):
  """Test generating chat response with code interpreter tool"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"
  generate_params = FAKE_GENERATE_PARAMS.copy()
  generate_params["tool_names"] = '["vertex_code_interpreter_tool"]'
  generate_params["prompt"] = "give me a pie chart of continents by land area"

  # Mock response from code interpreter tool
  mock_tool_response = {
    "generated_code": "print('test code')",
    "execution_result": "test result", 
    "execution_error": None,
    "output_files": [
      {
        "name": "plot.png",
        # Real response would have actual base64 data
        "contents": "base64encodedstring"
      }
    ]
  }

  # Mock both the code interpreter tool and summary generation
  with mock.patch(
    "services.agents.agent_tools.vertex_code_interpreter_tool",
    return_value=mock_tool_response
  ), mock.patch(
    "routes.chat.generate_chat_summary",
    return_value="Test Chart Generation Chat"
  ), mock.patch(
    "services.llm_generate.llm_chat",
    return_value="Test Chart Generation Chat"
  ):
    resp = client_with_emulator.post(url, json=generate_params)

    assert resp.status_code == 200
    json_response = resp.json()
    user_chat = json_response["data"]

    # Get the new entries (last 4 entries in history)
    new_entries = user_chat["history"][-4:]

    # Check user prompt
    assert new_entries[0] == {
      CHAT_HUMAN: generate_params["prompt"]
    }, "First new entry should be user prompt"

    # Check AI response containing code and result
    expected_response = (
      "Code generated\n\n"
      "```print('test code')```"
      "Execution result from the code: "
      "```test result```"
    )
    assert new_entries[1] == {
      CHAT_AI: expected_response
    }, "Second new entry should be AI response with code"

    # Check file entries
    assert new_entries[2] == {
      CHAT_FILE: "plot.png"
    }, "Third new entry should be file name"

    assert new_entries[3] == {
      CHAT_FILE_BASE64: "base64encodedstring"
    }, "Fourth new entry should be file content"

    # If this was a new chat with no title, verify the title was set
    chat = UserChat.find_by_id(chatid)
    if not chat.title:
      assert user_chat["title"] == "Test Chart Generation Chat"

def test_generate_chat_summary(create_user, create_chat, client_with_emulator):
  """Test the generate_summary endpoint"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate_summary"

  # Test successful summary generation
  with mock.patch(
      "services.llm_generate.generate_chat_summary",
      return_value="Test Summary"
  ), mock.patch(
      "services.llm_generate.llm_chat",
      return_value="Test Summary"
  ):
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
  assert "not found" in json_response["message"].lower(), \
    "Error message indicates not found"
  assert json_response["data"] is None, "Error response has no data"

def test_generate_chat_summary_error(
    create_user,
    create_chat,
    client_with_emulator
):
  """Test generate_summary when summary generation fails"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate_summary"

  with mock.patch(
      "routes.chat.generate_chat_summary",
      side_effect=Exception("Summary generation failed")
  ):
    resp = client_with_emulator.post(url)

  assert resp.status_code == 500, "Failed summary generation returns 500"
  json_response = resp.json()
  assert json_response["success"] is False, "Error response indicates failure"
  assert "summary generation failed" in json_response["message"].lower(), \
    "Error message describes failure"
  assert json_response["data"] is None, "Error response has no data"

def test_chat_generate_adds_missing_title(
    create_user,
    create_chat,
    client_with_emulator
):
  """Test that generating a chat response adds a title if missing"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"

  # First remove the title
  chat = UserChat.find_by_id(chatid)
  chat.title = ""
  chat.save()

  with mock.patch(
      "routes.chat.llm_chat",
      return_value=FAKE_GENERATE_RESPONSE
  ), mock.patch(
      "services.llm_generate.generate_chat_summary",
      return_value="Test Summary"
  ), mock.patch(
      "services.llm_generate.llm_chat",
      return_value="Test Summary"
  ):
    resp = client_with_emulator.post(url, json=FAKE_GENERATE_PARAMS)

    json_response = resp.json()
    assert resp.status_code == 200
    chat_data = json_response.get("data")

    # Verify chat response was generated
    assert chat_data["history"][-2] == {
      CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]
    }
    assert chat_data["history"][-1] == {
      CHAT_AI: FAKE_GENERATE_RESPONSE
    }

    # Verify summary was generated and set as title
    assert chat_data["title"] == "Test Summary"

    # Verify chat was saved to database with summary
    updated_chat = UserChat.find_by_id(chatid)
    assert updated_chat.title == "Test Summary"

def test_chat_generate_keeps_existing_title(
    create_user,
    create_chat,
    client_with_emulator
):
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
    assert chat_data["history"][-2] == {
      CHAT_HUMAN: FAKE_GENERATE_PARAMS["prompt"]
    }
    assert chat_data["history"][-1] == {
      CHAT_AI: FAKE_GENERATE_RESPONSE
    }

    # Verify title was preserved and summary was not generated
    assert chat_data["title"] == "Existing Title"
    assert not mock_summary.called, "Summary not generated for existing title"

    # Verify chat in database still has original title
    updated_chat = UserChat.find_by_id(chatid)
    assert updated_chat.title == "Existing Title"

def test_get_chat_llm_list(client_with_emulator):
  """Test getting basic chat LLM list"""
  url = f"{api_url}/chat_types"

  removed_model = "VertexAI-Gemini-Pro"
  def mock_is_model_enabled_for_user(model_id, user_data):
    if model_id == removed_model:
      return False
    return True

  with mock.patch("config.model_config.ModelConfig.is_model_enabled_for_user",
                 side_effect=mock_is_model_enabled_for_user):

    # Test getting all models
    resp = client_with_emulator.get(url)
    assert resp.status_code == 200, "Status 200"
    json_response = resp.json()
    assert json_response["success"] is True
    assert len(json_response["data"]) > 0

    # Verify response contains only model IDs
    for model in json_response["data"]:
      assert isinstance(model, str), "Model entries should be strings (IDs)"
      assert model != removed_model, "Disabled model should not be included"

def test_get_chat_llm_details(client_with_emulator):
  """Test getting detailed chat LLM information"""
  url = f"{api_url}/chat_types/details"

  # Mock the model config to return test data
  test_model_config = {
    "name": "Test Chat Model",
    "description": "A test chat model",
    "capabilities": ["chat"],
    "date_added": "2024-01-01",
    "is_multi": False,
    "model_params": {
      "temperature": 0.7,
      "max_tokens": 1000
    }
  }

  test_provider_config = {
    "model_params": {
      "temperature": 0.5,  # This should be overridden by model config
      "top_p": 0.9  # This should be preserved
    }
  }

  def mock_get_model_config(model_id):
    return test_model_config

  def mock_get_model_provider_config(model_id):
    return "test_provider", test_provider_config

  def mock_is_model_enabled_for_user(model_id, user_data):
    return True

  with mock.patch("config.model_config.ModelConfig.get_model_config",
                 side_effect=mock_get_model_config), \
       mock.patch("config.model_config.ModelConfig.get_model_provider_config",
                 side_effect=mock_get_model_provider_config), \
       mock.patch("config.model_config.ModelConfig.is_model_enabled_for_user",
                 side_effect=mock_is_model_enabled_for_user):

    # Test getting all models
    resp = client_with_emulator.get(url)
    assert resp.status_code == 200, "Status 200"
    json_response = resp.json()
    assert json_response["success"] is True
    assert len(json_response["data"]) > 0

    # Verify model details structure
    model = json_response["data"][0]
    assert "id" in model
    assert model["name"] == test_model_config["name"]
    assert model["description"] == test_model_config["description"]
    assert model["capabilities"] == test_model_config["capabilities"]
    assert model["date_added"] == test_model_config["date_added"]
    assert model["is_multi"] == test_model_config["is_multi"]

    # Verify merged model parameters
    assert "model_params" in model
    assert model["model_params"]["temperature"] == 0.7  # From model config
    assert model["model_params"]["top_p"] == 0.9  # From provider config
    assert model["model_params"]["max_tokens"] == 1000  # From model config

def test_chat_llm_multimodal_filter(client_with_emulator):
  """Test multimodal filtering for both chat LLM endpoints"""
  base_url = f"{api_url}/chat_types"

  def mock_is_model_enabled_for_user(model_id, user_data):
    return True

  with mock.patch("config.model_config.ModelConfig.is_model_enabled_for_user",
                 side_effect=mock_is_model_enabled_for_user):
    # Test basic list endpoint
    resp = client_with_emulator.get(base_url, params={"is_multimodal": True})
    assert resp.status_code == 200
    json_response = resp.json()
    assert json_response["success"] is True

    # Test details endpoint
    details_url = f"{base_url}/details"
    params = {"is_multimodal": True}
    resp = client_with_emulator.get(details_url, params=params)
    assert resp.status_code == 200
    json_response = resp.json()
    assert json_response["success"] is True
    assert all(model["is_multi"] for model in json_response["data"])


@pytest.mark.asyncio
async def test_chat_generate_with_query_engine(create_user, create_chat,
                                               create_engine,
                                               client_with_emulator):
  """Test generating chat response with query engine"""
  chatid = CHAT_EXAMPLE["id"]
  url = f"{api_url}/{chatid}/generate"

  # Test parameters as JSON
  test_params = {
    "prompt": FAKE_GENERATE_PARAMS["prompt"],
    "llm_type": FAKE_GENERATE_PARAMS["llm_type"],
    "query_engine_id": create_engine.id,
    "query_filter": {"key": "value"}
  }

  # Mock query results
  mock_references = [
    QueryReference(
      query_engine_id=create_engine.id,
      query_engine=create_engine.name,
      document_id="doc1",
      document_url="http://test.com/doc1",
      document_text="Test reference text",
      modality="text",
      chunk_id="chunk1"
    )
  ]
  mock_content_files = [
    DataSourceFile(
      gcs_path="gs://bucket/image1.jpg",
      mime_type="image/jpeg"
    )
  ]

  with mock.patch("routes.chat.query_generate_for_chat",
                 return_value=(mock_references, mock_content_files)), \
       mock.patch("routes.chat.llm_chat",
                 return_value=FAKE_GENERATE_RESPONSE):
    resp = client_with_emulator.post(url, json=test_params)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  chat_data = json_response.get("data")

  # Verify chat history includes query engine and references
  history = chat_data["history"]
  assert any(CHAT_SOURCE in entry for entry in history), \
    "Chat history includes source"
  assert any(CHAT_QUERY_REFERENCES in entry for entry in history), \
    "Chat history includes references"
