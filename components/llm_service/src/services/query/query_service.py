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
Query Engine Service
"""
import tempfile
import os
from typing import List, Optional, Tuple, Dict
from common.utils.logging_handler import Logger
from common.models import (UserQuery, QueryResult, QueryEngine,
                           QueryDocument,
                           QueryReference, QueryDocumentChunk,
                           BatchJobModel)
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError)
from common.utils.http_exceptions import InternalServerError
from utils.errors import NoDocumentsIndexedException
from google.cloud import storage
from services import llm_generate
from services.query import query_prompts, embeddings
from services.query import vector_store
from services.query.vector_store import VectorStore
from services.query.data_source import DataSource

from config import (PROJECT_ID, DEFAULT_QUERY_CHAT_MODEL,
                    DEFAULT_QUERY_EMBEDDING_MODEL)

# pylint: disable=broad-exception-caught

Logger = Logger.get_logger(__file__)

async def query_generate(
            user_id: str,
            prompt: str,
            q_engine: QueryEngine,
            llm_type: Optional[str] = DEFAULT_QUERY_CHAT_MODEL,
            user_query: Optional[UserQuery] = None) -> \
                Tuple[QueryResult, List[QueryReference]]:
  """
  Execute a query over a query engine

  Args:
    user_id:
    prompt: the text prompt to pass to the query engine
    q_engine: the name of the query engine to use
    llm_type (optional): chat model to use for query
    user_query (optional): an existing user query for context

  Returns:
    QueryResult: the query result object

  Raises:
    ResourceNotFoundException if the named query engine doesn't exist
  """
  Logger.info(f"Executing query: "
              f"llm_type=[{llm_type}], "
              f"user_id=[{user_id}], "
              f"prompt=[{prompt}], q_engine=[{q_engine.name}], "
              f"user_query=[{user_query}]")
  # get doc context for question
  query_references = await query_search(q_engine, prompt)

  # generate question prompt for chat model
  question_prompt = query_prompts.question_prompt(prompt, query_references)

  # send question prompt to model
  question_response = await llm_generate.llm_chat(question_prompt, llm_type)

  # save query result
  query_ref_ids = []
  for ref in query_references:
    query_reference = QueryReference(
      query_engine_id=q_engine.id,
      query_engine=q_engine.name,
      document_id=ref["document_id"],
      chunk_id=ref["chunk_id"]
    )
    query_reference.save()
    query_ref_ids.append(query_reference.id)

  query_result = QueryResult(query_engine_id=q_engine.id,
                             query_engine=q_engine.name,
                             query_refs=query_ref_ids,
                             response=question_response)
  query_result.save()

  # save user query history
  if user_query is None:
    user_query = UserQuery(user_id=user_id,
                           query_engine_id=q_engine.id)
    user_query.save()
  user_query.update_history(prompt, question_response, query_references)

  return query_result, query_references


async def query_search(q_engine: QueryEngine,
                       query_prompt: str) -> List[dict]:
  """
  For a query prompt, retrieve text chunks with doc references
  from matching documents.
                       
  Args:
    q_engine: QueryEngine to search
    query_prompt (str):  user query

  Returns:
    list of dicts containing summarized query results, with:
      "document_id": id of QueryDocument for reference
      "document_url": url of document containing reference
      "document_text": text of document containing the grounding for the query 
      "chunk_id": id of QueryDocumentChunk containing the reference
                       
  """
  Logger.info(f"Retrieving doc references for q_engine=[{q_engine.name}], "
              f"query_prompt=[{query_prompt}]")
  # generate embeddings for prompt
  query_embeddings = embeddings.encode_texts_to_embeddings([query_prompt])

  qe_vector_store = vector_store.from_query_engine(q_engine)
  match_indexes_list = qe_vector_store.find_neighbors(q_engine,
                                                      query_embeddings)

  # assemble document chunk matches from match indexes
  query_references = []
  match_indexes = match_indexes_list[0]
  for match in match_indexes:
    doc_chunk = QueryDocumentChunk.find_by_index(q_engine.id, int(match.id))
    if doc_chunk is None:
      raise ResourceNotFoundException(
        f"Missing doc chunk match index {match.id} q_engine {q_engine.name}")
    query_doc = QueryDocument.find_by_id(doc_chunk.query_document_id)
    if query_doc is None:
      raise ResourceNotFoundException(
        f"Query doc {doc_chunk.query_document_id} q_engine {q_engine.name}")
    query_ref = {
      "document_id": query_doc.id,
      "document_url": query_doc.doc_url,
      "document_text": doc_chunk.text,
      "chunk_id": doc_chunk.id
    }
    query_references.append(query_ref)

  Logger.info(f"Retrieved {len(query_references)} "
              f"references={query_references}")
  return query_references


def batch_build_query_engine(request_body: Dict, job: BatchJobModel) -> Dict:
  """
  Handle a batch job request for query engine build.

  Args:
    request_body: dict of query engine build params
    job: BatchJobModel model object
  Returns:
    dict containing job meta data
  """
  doc_url = request_body.get("doc_url")
  query_engine = request_body.get("query_engine")
  user_id = request_body.get("user_id")
  is_public = request_body.get("is_public")
  llm_type = request_body.get("llm_type")

  Logger.info(f"Starting batch job for {query_engine} job id {job.id}")

  q_engine, docs_processed, docs_not_processed = \
      query_engine_build(doc_url, query_engine, user_id, is_public, llm_type)

  # update result data in batch job model
  docs_processed_urls = [doc.doc_url for doc in docs_processed]
  result_data = {
    "query_engine_id": q_engine.id,
    "docs_processed": docs_processed_urls,
    "docs_not_processed": docs_not_processed
  }
  job.result_data = result_data
  job.save(merge=True)

  Logger.info(f"Completed batch job query engine build for {query_engine}")

  return result_data


def query_engine_build(doc_url: str, query_engine: str, user_id: str,
                       is_public: Optional[bool] = True,
                       llm_type: Optional[str] = "") -> \
                       Tuple[str, List[QueryDocument], List[str]]:
  """
  Build a new query engine. NOTE currently supports only Vertex
   TextEmbeddingModel for embeddings.

  Args:
    doc_url: the URL to the set of documents to be indexed
    query_engine: the name of the query engine to create
    user_id: user id of engine creator
    is_public: is query engine publicly usable?
    llm_type: LLM used for query embeddings (currently not used)

  Returns:
    Tuple of QueryEngine id, list of QueryDocument objects of docs processed,
      list of urls of docs not processed

  Raises:
    ValidationError if the named query engine already exists
  """
  q_engine = QueryEngine.find_by_name(query_engine)
  if q_engine is not None:
    raise ValidationError(f"Query engine {query_engine} already exists")

  # create model
  llm_type = DEFAULT_QUERY_EMBEDDING_MODEL
  q_engine = QueryEngine(name=query_engine,
                         created_by=user_id,
                         llm_type=llm_type,
                         is_public=is_public)
  q_engine.save()

  # build document index
  try:
    docs_processed, docs_not_processed = build_doc_index(doc_url, query_engine)
  except Exception as e:
    # delete query engine model if build unsuccessful
    QueryDocument.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()
    QueryDocumentChunk.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()
    QueryEngine.delete_by_id(q_engine.id)
    raise InternalServerError(e) from e

  Logger.info(f"Completed query engine build for {query_engine}")

  return q_engine, docs_processed, docs_not_processed


def build_doc_index(doc_url: str, query_engine: str) -> \
        Tuple[List[QueryDocument], List[str]]:
  """
  Build the document index.
  Supports only GCS URLs initially, containing PDF files.

  Args:
    doc_url: URL pointing to folder of documents
    query_engine: the query engine to

  Returns:
    Tuple of list of QueryDocument objects of docs processed,
      list of urls of docs not processed
  """
  q_engine = QueryEngine.find_by_name(query_engine)
  if q_engine is None:
    raise ResourceNotFoundException(f"cant find query engine {query_engine}")

  storage_client = storage.Client(project=PROJECT_ID)

  qe_vector_store = vector_store.from_query_engine(q_engine)

  try:
    # process docs at url and upload embeddings to vector store
    docs_processed, docs_not_processed = process_documents(
      doc_url, qe_vector_store, q_engine, storage_client)

    # make sure we actually processed some docs
    if len(docs_processed) == 0:
      raise NoDocumentsIndexedException(
          f"Failed to process any documents at url {doc_url}")

    # deploy vectore store (e.g. create endpoint)
    qe_vector_store.deploy()

    return docs_processed, docs_not_processed

  except Exception as e:
    Logger.error(f"Error creating doc index {e}")
    raise InternalServerError(str(e)) from e


def process_documents(doc_url: str, qe_vector_store: VectorStore,
                       q_engine: QueryEngine, storage_client) -> \
                       Tuple[List[QueryDocument], List[str]]:
  """
  Process docs in data source and upload embeddings to vector store
  Returns:
     Tuple of list of QueryDocument objects for docs processed,
        list of doc urls of docs not processed
  """
  data_source = DataSource(storage_client)
  docs_processed = []
  with tempfile.TemporaryDirectory() as temp_dir:
    doc_filepaths = data_source.download_documents(doc_url, temp_dir)

    # counter for unique index ids
    index_base = 0

    for doc_name, index_doc_url, doc_filepath in doc_filepaths:
      text_chunks = data_source.chunk_document(doc_name,
                                               index_doc_url,
                                               doc_filepath)

      if text_chunks is None:
        # unable to process this doc; skip
        continue

      # generate embedding data and store in local dir
      new_index_base = \
          qe_vector_store.index_document(doc_name, text_chunks, index_base)

      # cleanup temp local file
      os.remove(doc_filepath)

      # store QueryDocument and QueryDocumentChunk models
      query_doc = QueryDocument(query_engine_id=q_engine.id,
                                query_engine=q_engine.name,
                                doc_url=index_doc_url,
                                index_start=index_base,
                                index_end=new_index_base)
      query_doc.save()

      for i in range(0, len(text_chunks)):
        query_doc_chunk = QueryDocumentChunk(
                                  query_engine_id=q_engine.id,
                                  query_document_id=query_doc.id,
                                  index=i+index_base,
                                  text=text_chunks[i])
        query_doc_chunk.save()

      index_base = new_index_base
      docs_processed.append(query_doc)

  return docs_processed, data_source.docs_not_processed


