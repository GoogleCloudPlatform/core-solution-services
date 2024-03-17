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
  Unit tests for Query Service
"""
# pylint: disable=unused-argument,redefined-outer-name,unused-import
import os
import pytest
from unittest import mock
from services.query.query_prompts import question_prompt
from services.query.query_prompt_config import QUESTION_PROMPT
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
                           QueryReference)
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

with mock.patch("common.utils.secrets.get_secret"):
  with mock.patch("langchain.chat_models.ChatOpenAI", new=mock.AsyncMock()):
    with mock.patch("langchain.llms.Cohere", new=mock.AsyncMock()):
      from config import DEFAULT_QUERY_CHAT_MODEL

@pytest.fixture
def create_query_reference(firestore_emulator, clean_firestore):
  query_reference_dict = QUERY_REFERENCE_EXAMPLE_1
  query_reference = QueryReference.from_dict(query_reference_dict)
  query_reference.save()
  return query_reference

@pytest.fixture
def create_query_reference_2(firestore_emulator, clean_firestore):
  query_reference_dict = QUERY_REFERENCE_EXAMPLE_2
  query_reference = QueryReference.from_dict(query_reference_dict)
  query_reference.save()
  return query_reference

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

FAKE_QUERY_PARAMS = QUERY_EXAMPLE

FAKE_GENERATE_RESPONSE = "test generation"


@pytest.mark.asyncio
def test_query_generate(create_query_reference,
                        create_query_reference_2):
  pass

def test_query_engine_build(create_query_reference,
                            create_query_reference_2):
  pass

def test_process_documents(create_query_reference,
                           create_query_reference_2):
  pass

def test_build_doc_index(create_query_reference,
                         create_query_reference_2):
  pass
