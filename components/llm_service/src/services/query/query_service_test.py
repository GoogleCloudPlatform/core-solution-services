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
  Unit tests for LLM Service endpoints
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,ungrouped-imports,unused-import
from copy import deepcopy
from pathlib import Path
import pytest
from typing import List, Optional
from unittest import mock
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
                                     QUERY_REFERENCE_EXAMPLE_1,
                                     QUERY_REFERENCE_EXAMPLE_2)
from common.models import (UserQuery, QueryResult, QueryEngine,
                           User, QueryDocument, QueryDocumentChunk,
                           QueryReference)
from common.models.llm_query import (QUERY_HUMAN,
                                     QUERY_AI_RESPONSE,
                                     QUERY_AI_REFERENCES)
from common.models.llm_query import QE_TYPE_INTEGRATED_SEARCH
from common.utils.logging_handler import Logger
from common.utils.config import set_env_var
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

with set_env_var("PG_HOST", ""):
  from config import get_model_config, ModelConfig, MODEL_CONFIG_PATH

from services.query.query_service import (query_generate,
                                          query_search,
                                          query_engine_build,
                                          process_documents,
                                          build_doc_index,
                                          retrieve_references)
from services.query.vector_store import VectorStore
from services.query.data_source import DataSource, DataSourceFile

Logger = Logger.get_logger(__file__)

@pytest.fixture
def restore_config():
  # restore global config
  mc = ModelConfig(MODEL_CONFIG_PATH)
  mc.load_model_config()
  get_model_config().copy_model_config(mc)
  Logger.info(f"*** model config: {mc.llm_models}")

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
def create_user(firestore_emulator, clean_firestore):
  user_dict = USER_EXAMPLE
  user = User.from_dict(user_dict)
  user.save()
  return user

@pytest.fixture
def create_engine(firestore_emulator, clean_firestore):
  query_engine_dict = QUERY_ENGINE_EXAMPLE
  q_engine = QueryEngine.from_dict(query_engine_dict)
  q_engine.save()
  return q_engine

@pytest.fixture
def create_user_query(firestore_emulator, clean_firestore):
  query_dict = USER_QUERY_EXAMPLE
  query = UserQuery.from_dict(query_dict)
  query.save()
  return query

@pytest.fixture
def create_query_result(firestore_emulator, clean_firestore):
  query_result_dict = QUERY_RESULT_EXAMPLE
  query_result = QueryResult.from_dict(query_result_dict)
  query_result.save()
  return query_result

@pytest.fixture
def create_query_docs(firestore_emulator, clean_firestore):
  query_doc1 = QueryDocument.from_dict(QUERY_DOCUMENT_EXAMPLE_1)
  query_doc1.save()
  query_doc2 = QueryDocument.from_dict(QUERY_DOCUMENT_EXAMPLE_2)
  query_doc2.save()
  query_doc3 = QueryDocument.from_dict(QUERY_DOCUMENT_EXAMPLE_3)
  query_doc3.save()
  return [query_doc1, query_doc2, query_doc3]

@pytest.fixture
def create_query_doc_chunks(firestore_emulator, clean_firestore):
  qdoc_chunk1 = QueryDocumentChunk.from_dict(QUERY_DOCUMENT_CHUNK_EXAMPLE_1)
  qdoc_chunk1.save()
  qdoc_chunk2 = QueryDocumentChunk.from_dict(QUERY_DOCUMENT_CHUNK_EXAMPLE_2)
  qdoc_chunk2.save()
  qdoc_chunk3 = QueryDocumentChunk.from_dict(QUERY_DOCUMENT_CHUNK_EXAMPLE_3)
  qdoc_chunk3.save()
  return [qdoc_chunk1, qdoc_chunk2, qdoc_chunk3]

FAKE_QUERY_PARAMS = QUERY_EXAMPLE

FAKE_GENERATE_RESPONSE = "test generation"

FAKE_GCS_PATH = "gs://fake-bucket"

DOC_NAME_1 = QUERY_DOCUMENT_EXAMPLE_1["doc_url"].split("/")[1]
DOC_NAME_2 = QUERY_DOCUMENT_EXAMPLE_2["doc_url"].split("/")[1]
DOC_NAME_3 = QUERY_DOCUMENT_EXAMPLE_3["doc_url"].split("/")[1]
DSF1 = DataSourceFile(DOC_NAME_1,
                      QUERY_DOCUMENT_EXAMPLE_1["doc_url"],
                      f"/tmp/{DOC_NAME_1}",
                      f"{FAKE_GCS_PATH}/{DOC_NAME_1}")
DSF2 = DataSourceFile(DOC_NAME_2,
                      QUERY_DOCUMENT_EXAMPLE_2["doc_url"],
                      f"/tmp/{DOC_NAME_2}",
                      f"{FAKE_GCS_PATH}/{DOC_NAME_2}")
DSF3 = DataSourceFile(DOC_NAME_3,
                      QUERY_DOCUMENT_EXAMPLE_3["doc_url"],
                      f"/tmp/{DOC_NAME_3}",
                      f"{FAKE_GCS_PATH}/{DOC_NAME_3}")


class FakeVectorStore(VectorStore):
  """ mock vector store class """
  def __init__(self):
    pass
  def init_index(self):
    pass
  async def index_document(self,
                           doc_name: str,
                           text_chunks: List[str],
                           index_base: int,
                           metadata: List[dict] = None) -> \
                            int:
    return 0
  async def index_document_multi(self,
                                 doc_name: str,
                                 doc_chunks: List[object],
                                 index_base: int) -> \
                                  int:
    return 0
  def deploy(self):
    pass
  def similarity_search(self, q_engine: QueryEngine,
                        query_embedding: List[float],
                        query_filter: Optional[str]) -> List[int]:
    return [0,1,2]

class FakeDataSource(DataSource):
  """ mock data source class """
  def __init__(self):
    self.docs_not_processed = [DSF3.src_url]

  def download_documents(self, doc_url: str, temp_dir: str) -> \
        List[DataSourceFile]:
    return [DSF1, DSF2, DSF3]

  def chunk_document(self, doc_name: str, doc_url: str,
                     doc_filepath: str) -> List[str]:
    if doc_url == QUERY_DOCUMENT_EXAMPLE_1["doc_url"]:
      chunk_list = [QUERY_DOCUMENT_CHUNK_EXAMPLE_1["text"]] # List of one string
    elif doc_url == QUERY_DOCUMENT_EXAMPLE_2["doc_url"]:
      chunk_list = [QUERY_DOCUMENT_CHUNK_EXAMPLE_2["text"]] # List of one string
    else:
      chunk_list = None
    return chunk_list, chunk_list

  def chunk_document_multi(self, doc_name:str, doc_url: str,
                            doc_filepath: str) -> List[str]:
    if doc_url == QUERY_DOCUMENT_EXAMPLE_1["doc_url"]:
      chunk_list = [{
        "image": "fake_val",
        "image_url": "fake_url",
        "text": ""
      }] # List of one dict
    elif doc_url == QUERY_DOCUMENT_EXAMPLE_2["doc_url"]:
      chunk_list = [{
        "image": "fake_val",
        "image_url": "fake_url",
        "text": ""
      }] # List of one dict
    else:
      chunk_list = None
    return chunk_list
    #SC240916: Change keys "text_chunks"-->"text", "image_b64"-->"image" DONE

@pytest.mark.asyncio
@mock.patch("services.query.query_service.llm_chat")
@mock.patch("services.query.query_service.query_search")
async def test_query_generate(mock_query_search, mock_llm_chat,
                        restore_config, create_engine, create_user,
                        create_query_result, create_query_reference,
                        create_query_reference_2):
  prompt = QUERY_EXAMPLE["prompt"]
  mock_query_search.return_value = [create_query_reference,
                                    create_query_reference_2]
  mock_llm_chat.return_value = FAKE_GENERATE_RESPONSE
  query_result, query_references = \
      await query_generate(create_user.id, prompt, create_engine)
  assert query_result.query_engine_id == create_engine.id
  assert query_result.prompt == prompt
  assert query_result.response == FAKE_GENERATE_RESPONSE
  assert len(query_references) == 2
  assert query_references[0] == create_query_reference
  assert query_references[1] == create_query_reference_2

@pytest.mark.asyncio
@mock.patch("services.query.query_service.llm_chat")
@mock.patch("services.query.query_service.query_search")
async def test_query_generate_continue(mock_query_search, mock_llm_chat,
                        restore_config, create_engine, create_user,
                        create_user_query,
                        create_query_result, create_query_reference,
                        create_query_reference_2):
  prompt = QUERY_EXAMPLE["prompt"]
  mock_query_search.return_value = [create_query_reference,
                                    create_query_reference_2]
  mock_llm_chat.return_value = FAKE_GENERATE_RESPONSE
  initial_history = deepcopy(create_user_query.history)
  initial_len = len(initial_history)
  Logger.info(f"initial history {initial_history}")
  query_result, query_references = \
      await query_generate(create_user.id,
                           prompt, create_engine,
                           user_query=create_user_query)
  assert query_result.query_engine_id == create_engine.id
  assert query_result.prompt == prompt
  assert query_result.response == FAKE_GENERATE_RESPONSE
  assert len(query_references) == 2
  assert query_references[0] == create_query_reference
  assert query_references[1] == create_query_reference_2

  # check user_query update
  query_history = create_user_query.reload().history
  Logger.info(f"updated history {query_history}")
  assert len(query_history) == initial_len + 3
  assert QUERY_HUMAN in query_history[initial_len]
  assert QUERY_AI_RESPONSE in query_history[initial_len + 1]
  assert QUERY_AI_REFERENCES in query_history[initial_len + 2]


@pytest.mark.asyncio
@mock.patch("services.query.query_service.embeddings.get_embeddings")
@mock.patch("services.query.query_service.vector_store_from_query_engine")
@mock.patch("services.query.query_service.get_top_relevant_sentences")
async def test_query_search(mock_get_top_relevant_sentences,
                            mock_get_vector_store, mock_get_embeddings,
                            create_engine, create_user, create_query_docs,
                            create_query_doc_chunks):
  # test llm service query search
  qdoc_chunk1 = create_query_doc_chunks[0]
  qdoc_chunk2 = create_query_doc_chunks[1]
  qdoc_chunk3 = create_query_doc_chunks[2]
  mock_get_embeddings.return_value = [True, True, True, True], [0,1,2,3]
  mock_get_vector_store.return_value = FakeVectorStore()
  mock_get_top_relevant_sentences.return_value = "test sentence"
  prompt = QUERY_EXAMPLE["prompt"]
  query_references = await query_search(create_engine, prompt)
  assert len(query_references) == len(create_query_doc_chunks)
  assert query_references[0].chunk_id == qdoc_chunk1.id
  assert query_references[1].chunk_id == qdoc_chunk2.id
  assert query_references[2].chunk_id == qdoc_chunk3.id

  # test integrated search
  doc_url = ""
  build_params = {
    "associated_engines": create_engine.name
  }
  q_engine_2, docs_processed, docs_not_processed = \
      await query_engine_build(doc_url, "test integrated search",
                               create_user.id,
                               query_engine_type=QE_TYPE_INTEGRATED_SEARCH,
                               params=build_params)

  assert docs_processed == []
  assert docs_not_processed == []
  query_references = \
      await retrieve_references(prompt, q_engine_2, create_user.id)
  assert len(query_references) == len(create_query_doc_chunks)
  assert query_references[0].chunk_id == qdoc_chunk1.id
  assert query_references[1].chunk_id == qdoc_chunk2.id
  assert query_references[2].chunk_id == qdoc_chunk3.id

# Test of query_engine_build function, with no optional input argument params
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.build_doc_index")
@mock.patch("services.query.query_service.vector_store_from_query_engine")
async def test_query_engine_build(mock_get_vector_store,
                                  mock_build_doc_index,
                                  create_query_docs,
                                  create_user):
  mock_get_vector_store.return_value = FakeVectorStore()
  mock_build_doc_index.return_value = (
      [create_query_docs[0], create_query_docs[1]],
      [create_query_docs[2]]
  )
  doc_url = FAKE_GCS_PATH
  q_engine, docs_processed, docs_not_processed = \
      await query_engine_build(doc_url,
                               QUERY_ENGINE_EXAMPLE["name"],
                               create_user.id)
  assert q_engine.created_by == create_user.id
  assert q_engine.name == QUERY_ENGINE_EXAMPLE["name"]
  assert q_engine.doc_url == doc_url
  assert docs_processed == [create_query_docs[0], create_query_docs[1]]
  assert docs_not_processed == [create_query_docs[2]]

  # test integrated search build
  doc_url = ""
  build_params = {
    "associated_engines": q_engine.name
  }
  q_engine_2, docs_processed, docs_not_processed = \
      await query_engine_build(doc_url,
                               "test integrated search",
                               create_user.id,
                               query_engine_type=QE_TYPE_INTEGRATED_SEARCH,
                               params=build_params)
  assert docs_processed == []
  assert docs_not_processed == []
  q_engine = QueryEngine.find_by_id(q_engine.id)
  assert q_engine.parent_engine_id == q_engine_2.id

# Test of query_engine_build function, with optional input argument params,
# which includes is_multimodal=True
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.build_doc_index")
@mock.patch("services.query.query_service.vector_store_from_query_engine")
async def test_query_engine_build_multi(mock_get_vector_store,
                                        mock_build_doc_index,
                                        create_query_docs,
                                        create_user):
  mock_get_vector_store.return_value = FakeVectorStore()
  mock_build_doc_index.return_value = (
      [create_query_docs[0], create_query_docs[1]],
      [create_query_docs[2]]
  )
  doc_url = FAKE_GCS_PATH
  build_params = {
    "is_multimodal": "True"
  }
  q_engine, docs_processed, docs_not_processed = \
      await query_engine_build(doc_url=doc_url,
                               query_engine=QUERY_ENGINE_EXAMPLE["name"],
                               user_id=create_user.id,
                               params=build_params)
  assert q_engine.created_by == create_user.id
  assert q_engine.name == QUERY_ENGINE_EXAMPLE["name"]
  assert q_engine.doc_url == doc_url
  assert q_engine.params["is_multimodal"].lower() ==\
    build_params["is_multimodal"].lower()
  assert docs_processed == [create_query_docs[0], create_query_docs[1]]
  assert docs_not_processed == [create_query_docs[2]]

  # test integrated search build
  doc_url = ""
  build_params = {
    "associated_engines": q_engine.name,
    "is_multimodal": "True"
  }
  q_engine_2, docs_processed, docs_not_processed =\
      await query_engine_build(doc_url=doc_url,
                               query_engine="test integrated search",
                               user_id=create_user.id,
                               query_engine_type=QE_TYPE_INTEGRATED_SEARCH,
                               params=build_params)
  assert docs_processed == []
  assert docs_not_processed == []
  q_engine = QueryEngine.find_by_id(q_engine.id)
  assert q_engine.parent_engine_id == q_engine_2.id

# Test of query_engine_build function, with optional input argument params,
# which includes is_multimodal=False
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.build_doc_index")
@mock.patch("services.query.query_service.vector_store_from_query_engine")
async def test_query_engine_build_textonly(mock_get_vector_store,
                                           mock_build_doc_index,
                                           create_query_docs,
                                           create_user):
  mock_get_vector_store.return_value = FakeVectorStore()
  mock_build_doc_index.return_value = (
      [create_query_docs[0], create_query_docs[1]],
      [create_query_docs[2]]
  )
  doc_url = FAKE_GCS_PATH
  build_params = {
    "is_multimodal": "False"
  }
  q_engine, docs_processed, docs_not_processed =\
      await query_engine_build(doc_url=doc_url,
                               query_engine=QUERY_ENGINE_EXAMPLE["name"],
                               user_id=create_user.id,
                               params=build_params)
  assert q_engine.created_by == create_user.id
  assert q_engine.name == QUERY_ENGINE_EXAMPLE["name"]
  assert q_engine.doc_url == doc_url
  assert q_engine.params["is_multimodal"].lower() ==\
    build_params["is_multimodal"].lower()
  assert docs_processed == [create_query_docs[0], create_query_docs[1]]
  assert docs_not_processed == [create_query_docs[2]]

  # test integrated search build
  doc_url = ""
  build_params = {
    "associated_engines": q_engine.name,
    "is_multimodal": "False"
  }
  q_engine_2, docs_processed, docs_not_processed = \
      await query_engine_build(doc_url=doc_url,
                               query_engine="test integrated search",
                               user_id=create_user.id,
                               query_engine_type=QE_TYPE_INTEGRATED_SEARCH,
                               params=build_params)
  assert docs_processed == []
  assert docs_not_processed == []
  q_engine = QueryEngine.find_by_id(q_engine.id)
  assert q_engine.parent_engine_id == q_engine_2.id

# Test of build_doc_index function, with no optional input argument
# is_multimodal (which defaults to False)
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.process_documents")
async def test_build_doc_index(mock_process_documents,
                               create_engine,
                               create_query_docs):
  doc_url = FAKE_GCS_PATH
  qe_vector_store = FakeVectorStore()
  mock_process_documents.return_value = (
      [create_query_docs[0], create_query_docs[1]],
      [create_query_docs[2]]
  )
  with mock.patch("google.cloud.storage.Client"):
    docs_processed, docs_not_processed = \
        await build_doc_index(doc_url=doc_url,
                              q_engine=create_engine,
                              qe_vector_store=qe_vector_store)
  assert docs_processed == [create_query_docs[0], create_query_docs[1]]
  assert docs_not_processed == [create_query_docs[2]]

# Test of build_doc_index function, with optional input argument
# is_multimodal=True
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.process_documents")
async def test_build_doc_index_multi(mock_process_documents,
                                     create_engine,
                                     create_query_docs):
  doc_url = FAKE_GCS_PATH
  qe_vector_store = FakeVectorStore()
  mock_process_documents.return_value = (
      [create_query_docs[0], create_query_docs[1]],
      [create_query_docs[2]]
  )
  with mock.patch("google.cloud.storage.Client"):
    docs_processed, docs_not_processed = \
        await build_doc_index(doc_url=doc_url,
                              q_engine=create_engine,
                              qe_vector_store=qe_vector_store,
                              is_multimodal=True)
  assert docs_processed == [create_query_docs[0], create_query_docs[1]]
  assert docs_not_processed == [create_query_docs[2]]

# Test of build_doc_index function, with optional input argument
# is_multimodal=False
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.process_documents")
async def test_build_doc_index_textonly(mock_process_documents,
                                        create_engine,
                                        create_query_docs):
  doc_url = FAKE_GCS_PATH
  qe_vector_store = FakeVectorStore()
  mock_process_documents.return_value = (
      [create_query_docs[0], create_query_docs[1]],
      [create_query_docs[2]]
  )
  with mock.patch("google.cloud.storage.Client"):
    docs_processed, docs_not_processed = \
        await build_doc_index(doc_url=doc_url,
                              q_engine=create_engine,
                              qe_vector_store=qe_vector_store,
                              is_multimodal=False)
  assert docs_processed == [create_query_docs[0], create_query_docs[1]]
  assert docs_not_processed == [create_query_docs[2]]

# Test of process_documents function, with no optional input argument
# is_multimodal (which defaults to False)
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.datasource_from_url")
async def test_process_documents(mock_get_datasource, create_engine):
  mock_get_datasource.return_value = FakeDataSource()
  doc_url = FAKE_GCS_PATH
  qe_vector_store = FakeVectorStore()
  Path(DSF1.local_path).touch()
  Path(DSF2.local_path).touch()
  docs_processed, docs_not_processed = \
      await process_documents(doc_url=doc_url,
                              qe_vector_store=qe_vector_store,
                              q_engine=create_engine,
                              storage_client=None)
  assert {doc.doc_url for doc in docs_processed} == {DSF1.src_url, DSF2.src_url}
  assert set(docs_not_processed) == {DSF3.src_url}

# Test of process_documents function, with optional input argument
# is_multimodal=True
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.datasource_from_url")
async def test_process_documents_multi(mock_get_datasource, create_engine):
  mock_get_datasource.return_value = FakeDataSource()
  doc_url = FAKE_GCS_PATH
  qe_vector_store = FakeVectorStore()
  Path(DSF1.local_path).touch()
  Path(DSF2.local_path).touch()
  docs_processed, docs_not_processed = \
      await process_documents(doc_url=doc_url,
                              qe_vector_store=qe_vector_store,
                              q_engine=create_engine,
                              storage_client=None,
                              is_multimodal=True)
  assert {doc.doc_url for doc in docs_processed} == {DSF1.src_url, DSF2.src_url}
  assert set(docs_not_processed) == {DSF3.src_url}

# Test of process_documents function, with optional input argument
# is_multimodal=False
# Uses same 3 example docs as other tests of this function
@pytest.mark.asyncio
@mock.patch("services.query.query_service.datasource_from_url")
async def test_process_documents_textonly(mock_get_datasource, create_engine):
  mock_get_datasource.return_value = FakeDataSource()
  doc_url = FAKE_GCS_PATH
  qe_vector_store = FakeVectorStore()
  Path(DSF1.local_path).touch()
  Path(DSF2.local_path).touch()
  docs_processed, docs_not_processed = \
      await process_documents(doc_url=doc_url,
                              qe_vector_store=qe_vector_store,
                              q_engine=create_engine,
                              storage_client=None,
                              is_multimodal=False)
  assert {doc.doc_url for doc in docs_processed} == \
         {DSF1.src_url, DSF2.src_url}
  assert set(docs_not_processed) == {DSF3.src_url}
