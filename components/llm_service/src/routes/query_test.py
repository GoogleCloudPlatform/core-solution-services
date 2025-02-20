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
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports,use-implicit-booleaness-not-comparison
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock

from testing.test_config import API_URL
from schemas.schema_examples import (QUERY_EXAMPLE,
                                     USER_QUERY_EXAMPLE,
                                     USER_EXAMPLE,
                                     QUERY_ENGINE_EXAMPLE,
                                     QUERY_DOCUMENT_EXAMPLE_1,
                                     QUERY_DOCUMENT_EXAMPLE_2,
                                     QUERY_DOCUMENT_EXAMPLE_3,
                                     QUERY_DOCUMENT_CHUNK_EXAMPLE_1,
                                     QUERY_DOCUMENT_CHUNK_EXAMPLE_2,
                                     QUERY_DOCUMENT_CHUNK_EXAMPLE_3,
                                     QUERY_RESULT_EXAMPLE,
                                     QUERY_REFERENCE_EXAMPLE_1)
from common.models import (UserQuery, QueryResult, QueryEngine,
                           User, QueryDocument, QueryDocumentChunk,
                           QueryReference, UserChat)
from common.models.llm_query import QE_TYPE_INTEGRATED_SEARCH
from common.utils.http_exceptions import add_exception_handlers
from common.utils.auth_service import validate_user
from common.utils.auth_service import validate_token
from common.utils.errors import ResourceNotFoundException
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from services.llm_generate import generate_chat_summary

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["GCP_PROJECT"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

with mock.patch("common.utils.secrets.get_secret"):
  with mock.patch("langchain.chat_models.ChatOpenAI", new=mock.AsyncMock()):
    with mock.patch("langchain.llms.Cohere", new=mock.AsyncMock()):
      from config import DEFAULT_QUERY_CHAT_MODEL

# assigning url
api_url = f"{API_URL}/query"

with mock.patch("common.utils.secrets.get_secret"):
  with mock.patch("kubernetes.config.load_incluster_config"):
    from routes.query import router

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

FAKE_QE_BUILD_RESPONSE = {
  "success": True,
  "message": "job created",
  "data": {
    "name": "fake_job_name",
    "status": "fake_job_status",
    "type": "query_engine_build"
  }
}

FAKE_QUERY_ENGINE_BUILD = {
  "doc_url": "http://fake-url",
  "query_engine": "query-engine-test",
  "llm_type": DEFAULT_QUERY_CHAT_MODEL,
  "description": "Test Description",
  "is_public": True
}

FAKE_GENERATE_RESPONSE = "test generation"

FAKE_QUERY_PARAMS = QUERY_EXAMPLE

FAKE_CHAT_SUMMARY = "Test chat summary"

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
def create_engine(client_with_emulator):
  query_engine_dict = QUERY_ENGINE_EXAMPLE
  q_engine = QueryEngine.from_dict(query_engine_dict)
  q_engine.save()


@pytest.fixture
def create_user_query(client_with_emulator):
  query_dict = USER_QUERY_EXAMPLE
  query = UserQuery.from_dict(query_dict)
  query.save()


@pytest.fixture
def create_query_result(client_with_emulator):
  query_result_dict = QUERY_RESULT_EXAMPLE
  query_result = QueryResult.from_dict(query_result_dict)
  query_result.save()


@pytest.fixture
def create_query_reference(client_with_emulator):
  query_reference_dict = QUERY_REFERENCE_EXAMPLE_1
  query_reference = QueryReference.from_dict(query_reference_dict)
  query_reference.save()
  return query_reference


@pytest.fixture
def create_query_docs(client_with_emulator):
  query_doc1 = QueryDocument.from_dict(QUERY_DOCUMENT_EXAMPLE_1)
  query_doc1.save()
  query_doc2 = QueryDocument.from_dict(QUERY_DOCUMENT_EXAMPLE_2)
  query_doc2.save()
  query_doc3 = QueryDocument.from_dict(QUERY_DOCUMENT_EXAMPLE_3)
  query_doc3.save()


@pytest.fixture
def create_query_doc_chunks(client_with_emulator):
  qdoc_chunk1 = QueryDocumentChunk.from_dict(QUERY_DOCUMENT_CHUNK_EXAMPLE_1)
  qdoc_chunk1.save()
  qdoc_chunk2 = QueryDocumentChunk.from_dict(QUERY_DOCUMENT_CHUNK_EXAMPLE_2)
  qdoc_chunk2.save()
  qdoc_chunk3 = QueryDocumentChunk.from_dict(QUERY_DOCUMENT_CHUNK_EXAMPLE_3)
  qdoc_chunk3.save()


@pytest.fixture
def create_user_chat(client_with_emulator):
  """Create a test user chat"""
  chat_dict = {
    "id": "fake-chat-id",
    "user_id": USER_EXAMPLE["id"],
    "llm_type": DEFAULT_QUERY_CHAT_MODEL,
    "title": "Test Chat",
    "history": []
  }
  chat = UserChat.from_dict(chat_dict)
  chat.save()
  return chat


def test_get_query_engine_list(create_engine, client_with_emulator):
  url = f"{api_url}"
  resp = client_with_emulator.get(url)
  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  saved_ids = [i.get("id") for i in json_response.get("data")]
  assert QUERY_ENGINE_EXAMPLE["id"] in saved_ids, "all data not retrieved"
  for i in json_response["data"]:
    if (i["id"] == QUERY_ENGINE_EXAMPLE["id"] and
        i["read_access_group"] ==
        QUERY_ENGINE_EXAMPLE["read_access_group"]):
      break
  else:
    assert False, "read access group not found"


def test_get_query_engine_urls(create_engine, create_query_docs,
                               client_with_emulator):
  q_engine_id = QUERY_ENGINE_EXAMPLE["id"]
  url = f"{api_url}/urls/{q_engine_id}"

  resp = client_with_emulator.get(url)
  json_response = resp.json()
  urls = json_response.get("data")
  assert resp.status_code == 200, "Status 200"
  assert QUERY_DOCUMENT_EXAMPLE_1["doc_url"] in urls, "doc1 retrieved"
  assert QUERY_DOCUMENT_EXAMPLE_2["doc_url"] in urls, "doc2 retrieved"
  assert QUERY_DOCUMENT_EXAMPLE_3["doc_url"] not in urls, "doc3 not retrieved"


def test_create_query_engine(create_user, client_with_emulator):
  url = f"{api_url}/engine"
  params = FAKE_QUERY_ENGINE_BUILD
  with mock.patch("routes.query.initiate_batch_job",
                  return_value=FAKE_QE_BUILD_RESPONSE):
    resp = client_with_emulator.post(url, json=params)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  query_engine_data = json_response.get("data")
  assert query_engine_data == FAKE_QE_BUILD_RESPONSE["data"]

  # test integrated search build
  params = {
    "query_engine": "query-engine-integrated-test",
    "doc_url": "",
    "description": "",
    "query_engine_type": QE_TYPE_INTEGRATED_SEARCH,
    "params": {
      "associated_engines": FAKE_QUERY_ENGINE_BUILD["query_engine"]
    }
  }
  with mock.patch("routes.query.initiate_batch_job",
                  return_value=FAKE_QE_BUILD_RESPONSE):
    resp = client_with_emulator.post(url, json=params)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  query_engine_data = json_response.get("data")
  assert query_engine_data == FAKE_QE_BUILD_RESPONSE["data"]

def test_get_query_engine(create_engine, client_with_emulator):
  qe_id = QUERY_ENGINE_EXAMPLE["id"]
  url = f"{api_url}/engine/{qe_id}"
  resp = client_with_emulator.get(url)
  json_response = resp.json()

  assert resp.status_code == 200, "Status 200"
  saved_id = json_response["data"]["id"]
  assert QUERY_ENGINE_EXAMPLE["id"] == saved_id, "all data not retrieved"
  saved_read_access_group = json_response["data"]["read_access_group"]
  assert QUERY_ENGINE_EXAMPLE["read_access_group"] == saved_read_access_group, \
    "all data not retrieved"

def test_update_query_engine(create_engine, client_with_emulator):
  qe_id = QUERY_ENGINE_EXAMPLE["id"]
  url = f"{api_url}/engine/{qe_id}"
  new_query_engine_fields = {
    "query_engine": QUERY_ENGINE_EXAMPLE["name"],
    "description": "New Engine Description",
    "read_access_group": "2024:11:40:190:203:B1",
    "doc_url": "",
  }
  resp = client_with_emulator.put(url, json=new_query_engine_fields)
  json_response = resp.json()

  assert resp.status_code == 200, "Status 200"

  url = f"{api_url}/engine/{qe_id}"
  resp = client_with_emulator.get(url)
  json_response = resp.json()

  assert resp.status_code == 200, "Status 200"
  saved_id = json_response["data"]["id"]
  assert QUERY_ENGINE_EXAMPLE["id"] == saved_id, "all data not retrieved"
  saved_read_access_group = json_response["data"]["read_access_group"]
  saved_description = json_response["data"]["description"]
  assert new_query_engine_fields["read_access_group"] == \
    saved_read_access_group, "all data not retrieved"
  assert new_query_engine_fields["description"] == \
    saved_description, "all data not retrieved"

@mock.patch("services.query.query_service.vector_store_from_query_engine")
def test_delete_query_engine_soft(mock_vector_store, create_user,
                                  create_engine, create_query_docs,
                                  create_query_doc_chunks,
                                  client_with_emulator):
  mock_vector_store = mock.Mock()
  mock_vector_store.delete.return_value = None
  q_engine_id = QUERY_ENGINE_EXAMPLE["id"]
  q_doc_id = QUERY_DOCUMENT_EXAMPLE_1["id"]
  q_chunk_id = QUERY_DOCUMENT_CHUNK_EXAMPLE_1["id"]
  url = f"{api_url}/engine/{q_engine_id}"

  query_engine_before = QueryEngine.find_by_id(q_engine_id)
  resp = client_with_emulator.delete(url, params={"hard_delete": False})
  json_response = resp.json()
  query_data = json_response.get("message")

  with pytest.raises(ResourceNotFoundException):
    QueryEngine.find_by_id(q_engine_id)
  with pytest.raises(ResourceNotFoundException):
    QueryDocument.find_by_id(q_doc_id)
  with pytest.raises(ResourceNotFoundException):
    QueryDocumentChunk.find_by_id(q_chunk_id)

  qdocs = QueryDocument.collection.filter(
      "query_engine_id", "==", q_engine_id).fetch()
  assert len(list(qdocs)) == 2

  qchunks = QueryDocumentChunk.collection.filter(
      "query_engine_id", "==", q_engine_id).fetch()
  assert len(list(qchunks)) == 3

  assert query_engine_before.name == QUERY_ENGINE_EXAMPLE["name"], "valid"
  assert resp.status_code == 200, "Status 200"
  assert query_data == (f"Successfully deleted query engine"
                        f" {q_engine_id}"), "Success"


@mock.patch("services.query.query_service.vector_store_from_query_engine")
def test_delete_query_engine_hard(mock_vector_store, create_user,
                                  create_engine, create_query_docs,
                                  create_query_doc_chunks,
                                  client_with_emulator):
  mock_vector_store = mock.Mock()
  mock_vector_store.delete.return_value = None
  q_engine_id = QUERY_ENGINE_EXAMPLE["id"]
  q_doc_id = QUERY_DOCUMENT_EXAMPLE_1["id"]
  q_chunk_id = QUERY_DOCUMENT_CHUNK_EXAMPLE_1["id"]
  url = f"{api_url}/engine/{q_engine_id}"

  query_engine_before = QueryEngine.find_by_id(q_engine_id)
  resp = client_with_emulator.delete(url)
  json_response = resp.json()
  query_data = json_response.get("message")

  with pytest.raises(ResourceNotFoundException):
    QueryEngine.find_by_id(q_engine_id)
  with pytest.raises(ResourceNotFoundException):
    QueryDocument.find_by_id(q_doc_id)
  with pytest.raises(ResourceNotFoundException):
    QueryDocumentChunk.find_by_id(q_chunk_id)

  qdocs = QueryDocument.collection.filter(
      "query_engine_id", "==", q_engine_id).fetch()
  assert list(qdocs) == []

  qchunks = QueryDocumentChunk.collection.filter(
      "query_engine_id", "==", q_engine_id).fetch()
  assert list(qchunks) == []

  assert query_engine_before.name == QUERY_ENGINE_EXAMPLE["name"], "valid"
  assert resp.status_code == 200, "Status 200"
  assert query_data == (f"Successfully deleted query engine"
                        f" {q_engine_id}"), "Success"


def test_query(create_user, create_engine,
               create_query_result, create_query_reference,
               client_with_emulator):
  q_engine_id = QUERY_ENGINE_EXAMPLE["id"]
  url = f"{api_url}/engine/{q_engine_id}"

  query_result = QueryResult.find_by_id(QUERY_RESULT_EXAMPLE["id"])
  fake_query_response = (query_result, [create_query_reference])
  with mock.patch("routes.query.query_generate",
                  return_value=fake_query_response):
    resp = client_with_emulator.post(url, json=FAKE_QUERY_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  query_data = json_response.get("data")
  assert query_data["query_result"]["id"] == QUERY_RESULT_EXAMPLE.get("id"), \
    "returned query result"
  test_query_ref_fields = create_query_reference.get_fields(remove_meta=True)
  QueryReference.remove_field_meta(query_data["query_references"][0])
  assert query_data["query_references"] == [test_query_ref_fields], \
    "returned query references"


def test_query_generate(create_user, create_engine, create_user_query,
                        create_query_result, create_query_reference,
                        client_with_emulator):
  query_id = USER_QUERY_EXAMPLE["id"]

  url = f"{api_url}/{query_id}"

  query_result = QueryResult.find_by_id(QUERY_RESULT_EXAMPLE["id"])
  fake_query_response = (query_result, [create_query_reference])
  with mock.patch("routes.query.query_generate",
                  return_value=fake_query_response):
    resp = client_with_emulator.post(url, json=FAKE_QUERY_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  query_data = json_response.get("data")
  assert query_data["query_result"]["id"] == QUERY_RESULT_EXAMPLE.get("id"), \
    "returned query result"
  test_query_ref_fields = create_query_reference.get_fields(remove_meta=True)
  QueryReference.remove_field_meta(query_data["query_references"][0])
  assert query_data["query_references"] == [test_query_ref_fields], \
    "returned query references"


def test_get_query(create_user, create_engine, create_user_query,
                   client_with_emulator):
  query_id = USER_QUERY_EXAMPLE["id"]
  url = f"{api_url}/{query_id}"
  resp = client_with_emulator.get(url)
  json_response = resp.json()

  assert resp.status_code == 200, "Status 200"
  saved_id = json_response.get("data").get("id")
  assert USER_QUERY_EXAMPLE["id"] == saved_id, "all data not retrieved"


def test_update_query(create_user, create_user_query, client_with_emulator):
  query_id = USER_QUERY_EXAMPLE["id"]
  url = f"{api_url}/{query_id}"
  update_params = {
    "title": "updated title"
  }
  resp = client_with_emulator.put(url, json=update_params)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"

  updated_query = UserQuery.find_by_id(query_id)
  assert updated_query.title == "updated title", "user query updated"


def test_delete_query(create_user, create_user_query, client_with_emulator):
  # test soft delete
  query_id = USER_QUERY_EXAMPLE["id"]
  url = f"{api_url}/{query_id}"

  resp = client_with_emulator.delete(url, params={"hard_delete": False})
  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"

  deleted_query = UserQuery.collection.filter("id", "in",
      [query_id]).filter("deleted_at_timestamp",
      "==", None).get()
  assert deleted_query is None

  # test hard delete
  query_dict = USER_QUERY_EXAMPLE
  query = UserQuery.from_dict(query_dict)
  query.save()

  resp = client_with_emulator.delete(url, params={"hard_delete": True})
  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"

  deleted_query = UserQuery.collection.filter("id", "in",
      [query_id]).get()
  assert deleted_query is None

def test_get_queries(create_user, create_user_query, client_with_emulator):
  url = f"{api_url}/user"
  resp = client_with_emulator.get(url)
  json_response = resp.json()

  assert resp.status_code == 200, "Status 200"
  saved_ids = [i.get("id") for i in json_response.get("data")]
  assert USER_QUERY_EXAMPLE["id"] in saved_ids, "all data not retrieved"

@mock.patch("routes.query.generate_chat_summary")
def test_query_with_chat_mode(mock_generate_summary,
                             create_user,
                             create_engine,
                             create_query_result,
                             create_query_reference,
                             client_with_emulator):
  """Test query endpoint with chat_mode enabled"""
  mock_generate_summary.return_value = FAKE_CHAT_SUMMARY

  q_engine_id = QUERY_ENGINE_EXAMPLE["id"]
  url = f"{api_url}/engine/{q_engine_id}"

  # Add chat_mode to query params
  query_params = FAKE_QUERY_PARAMS.copy()
  query_params["chat_mode"] = True

  query_result = QueryResult.find_by_id(QUERY_RESULT_EXAMPLE["id"])
  fake_query_response = (query_result, [create_query_reference])

  with mock.patch("routes.query.query_generate",
                  return_value=fake_query_response):
    resp = client_with_emulator.post(url, json=query_params)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"

  query_data = json_response.get("data")

  # Verify query result and references
  assert query_data["query_result"]["id"] == QUERY_RESULT_EXAMPLE.get("id"), \
    "returned query result"
  test_query_ref_fields = create_query_reference.get_fields(remove_meta=True)
  QueryReference.remove_field_meta(query_data["query_references"][0])
  assert query_data["query_references"] == [test_query_ref_fields], \
    "returned query references"

  # Verify chat was created
  assert "user_chat_id" in query_data, "chat id returned"
  assert "user_chat" in query_data, "chat data returned"

  chat_data = query_data["user_chat"]
  assert chat_data["user_id"] == USER_EXAMPLE["id"], "chat has correct user"
  assert chat_data["llm_type"] == query_params.get("llm_type", None), \
    "chat has correct llm type"
  assert chat_data["title"] == FAKE_CHAT_SUMMARY, "chat has summary as title"

  # Verify chat history
  assert len(chat_data["history"]) > 0, "chat has history entries"

  # Verify chat exists in database
  chat = UserChat.find_by_id(query_data["user_chat_id"])
  assert chat is not None, "chat was saved to database"
  assert chat.title == FAKE_CHAT_SUMMARY, "chat title was saved"
  assert len(chat.history) > 0, "chat history was saved"

def test_query_without_chat_mode(create_user,
                                create_engine,
                                create_query_result,
                                create_query_reference,
                                client_with_emulator):
  """Test query endpoint with chat_mode disabled"""
  q_engine_id = QUERY_ENGINE_EXAMPLE["id"]
  url = f"{api_url}/engine/{q_engine_id}"

  # Explicitly disable chat mode
  query_params = FAKE_QUERY_PARAMS.copy()
  query_params["chat_mode"] = False

  query_result = QueryResult.find_by_id(QUERY_RESULT_EXAMPLE["id"])
  fake_query_response = (query_result, [create_query_reference])

  with mock.patch("routes.query.query_generate",
                  return_value=fake_query_response):
    resp = client_with_emulator.post(url, json=query_params)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"

  query_data = json_response.get("data")

  # Verify no chat data returned
  assert "user_chat_id" not in query_data, "no chat id returned"
  assert "user_chat" not in query_data, "no chat data returned"

  # Verify normal query data returned
  assert query_data["query_result"]["id"] == QUERY_RESULT_EXAMPLE.get("id"), \
    "returned query result"
  test_query_ref_fields = create_query_reference.get_fields(remove_meta=True)
  QueryReference.remove_field_meta(query_data["query_references"][0])
  assert query_data["query_references"] == [test_query_ref_fields], \
    "returned query references"
