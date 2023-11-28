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
from numpy.linalg import norm
import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Dict
from google.cloud.exceptions import Conflict
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
from services import llm_generate, embeddings
from services.query import query_prompts
from services.query.vector_store import (VectorStore,
                                         MatchingEngineVectorStore,
                                         PostgresVectorStore)
from services.query.data_source import DataSource
from services.query.web_datasource import WebDataSource
from utils.html_helper import html_to_text, html_to_sentence_list
from config import (PROJECT_ID, REGION, DEFAULT_QUERY_CHAT_MODEL,
                    DEFAULT_QUERY_EMBEDDING_MODEL)
from config.vector_store_config import (DEFAULT_VECTOR_STORE,
                                        VECTOR_STORE_LANGCHAIN_PGVECTOR,
                                        VECTOR_STORE_MATCHING_ENGINE)

# pylint: disable=broad-exception-caught

Logger = Logger.get_logger(__file__)

VECTOR_STORES = {
  VECTOR_STORE_MATCHING_ENGINE: MatchingEngineVectorStore,
  VECTOR_STORE_LANGCHAIN_PGVECTOR: PostgresVectorStore
}

async def query_generate(
            user_id: str,
            prompt: str,
            q_engine: QueryEngine,
            llm_type: Optional[str] = None,
            user_query: Optional[UserQuery] = None,
            sentence_references: bool = True) -> \
                Tuple[QueryResult, List[dict]]:
  """
  Execute a query over a query engine

  The rule for determining the model used for question generation
    model is:
    if llm_type is passed as an arg use it
    else if llm_type is set in query engine use that
    else use the default query chat model

  Args:
    user_id: user id if user making query
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
  query_references = await query_search(
      q_engine, prompt, sentence_references=sentence_references)

  # generate question prompt for chat model
  question_prompt = query_prompts.question_prompt(prompt, query_references)

  # determine question generation model
  if llm_type is None:
    if q_engine.llm_type is not None:
      llm_type = q_engine.llm_type
    else:
      llm_type = DEFAULT_QUERY_CHAT_MODEL

  # send question prompt to model
  # TODO: pass user_query history to model as context for generation.
  #       This requires refactoring the llm_chat method as it takes a
  #       UserChat model now.  Instead it should take a chat history.
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
                       query_prompt: str,
                       sentence_references: bool = False) -> List[dict]:
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
  status, query_embeddings = embeddings.get_embeddings([query_prompt],
                                               q_engine.embedding_type)
  query_embedding = query_embeddings[0]

  # retrieve indexes of relevant document chunks from vector store
  qe_vector_store = vector_store_from_query_engine(q_engine)
  match_indexes_list = qe_vector_store.similarity_search(q_engine,
                                                         query_embedding)
  query_references = []

  # Assemble document chunk references from vector store indexes
  for match in match_indexes_list:
    doc_chunk = QueryDocumentChunk.find_by_index(q_engine.id, match)
    if doc_chunk is None:
      raise ResourceNotFoundException(
        f"Missing doc chunk match index {match} q_engine {q_engine.name}")

    query_doc = QueryDocument.find_by_id(doc_chunk.query_document_id)
    if query_doc is None:
      raise ResourceNotFoundException(
        f"Query doc {doc_chunk.query_document_id} q_engine {q_engine.name}")

    clean_text = doc_chunk.clean_text
    if not clean_text:
      clean_text = html_to_text(doc_chunk.text)

    if sentence_references:
      # Assemble sentences from a document chunk. Currently it gets the
      # sentences from the top-ranked document chunk.
      sentences = doc_chunk.sentences

      if not sentences or len(sentences) == 0:
        sentences = html_to_sentence_list(doc_chunk.text)
      # Remove empty sentences.
      sentences = [x for x in sentences if x.strip() != ""]

      # Only update clean_text when sentences is not empty.
      Logger.info(f"sentences = {sentences}")
      if sentences and len(sentences) > 0:
        top_sentences = get_top_relevant_sentences(
            q_engine, query_embeddings, sentences,
            expand_neighbors=2, highlight_top_sentence=True)
        clean_text = " ".join(top_sentences)

    query_references.append({
      "document_id": query_doc.id,
      "document_url": query_doc.doc_url,
      "document_text": clean_text,
      "chunk_id": doc_chunk.id
    })

  # Logger.info(f"Retrieved {len(query_references)} "
  #             f"references={query_references}")
  return query_references

def get_top_relevant_sentences(q_engine, query_embeddings,
    sentences, expand_neighbors=2, highlight_top_sentence=False) -> list:

  status, sentence_embeddings = embeddings.get_embeddings(sentences,
                                                  q_engine.embedding_type)
  similarity_scores = get_similarity(query_embeddings, sentence_embeddings)
  Logger.info("Similarity scores of query_embeddings and sentence_embeddings: "
              f"{len(similarity_scores)}")

  top_sentence_index = np.argmax(similarity_scores)
  start_index = top_sentence_index - expand_neighbors
  end_index = top_sentence_index + expand_neighbors + 1

  if highlight_top_sentence:
    sentences[top_sentence_index] = \
        "<b>" + sentences[top_sentence_index] + "</b>"

  start_index = max(start_index, 0)
  end_index = min(end_index, len(similarity_scores))

  return sentences[start_index:end_index]

def get_similarity(query_embeddings, sentence_embeddings) -> list:
  query_df = pd.DataFrame(query_embeddings.transpose())
  sentence_df = pd.DataFrame(sentence_embeddings)

  cos_sim = []
  for index, row in sentence_df.iterrows():
    x = row
    y = query_df
    # calculate the cosine similiarity
    cosine = np.dot(x,y) / (norm(x) * norm(y))
    cos_sim.append(cosine[0])

  return cos_sim


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
  embedding_type = request_body.get("embedding_type")
  vector_store_type = request_body.get("vector_store")

  Logger.info(f"Starting batch job for query engine [{query_engine}] "
              f"job id [{job.id}]")
  Logger.info(f"doc_url: [{doc_url}] user id: [{user_id}]")
  Logger.info(f"embedding type: [{embedding_type}]")
  Logger.info(f"vector store type: [{vector_store_type}]")

  q_engine, docs_processed, docs_not_processed = \
      query_engine_build(doc_url, query_engine, user_id, is_public,
                         llm_type, embedding_type, vector_store_type)

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
                       llm_type: Optional[str] = None,
                       embedding_type: Optional[str] = None,
                       vector_store_type: Optional[str] = None) -> \
                       Tuple[str, List[QueryDocument], List[str]]:
  """
  Build a new query engine. NOTE currently supports only Vertex
   TextEmbeddingModel for embeddings.

  Args:
    doc_url: the URL to the set of documents to be indexed
    query_engine: the name of the query engine to create
    user_id: user id of engine creator
    is_public: is query engine publicly usable?
    llm_type: llm used for query answer generation
    embedding_type: LLM used for query embeddings
    vector_store_type: vector store type (from config.vector_store_config)

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
  if llm_type is None:
    llm_type = DEFAULT_QUERY_CHAT_MODEL

  if embedding_type is None:
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL

  q_engine = QueryEngine(name=query_engine,
                         created_by=user_id,
                         llm_type=llm_type,
                         embedding_type=embedding_type,
                         vector_store=vector_store_type,
                         is_public=is_public)

  # retrieve vector store class and store type in q_engine
  qe_vector_store = vector_store_from_query_engine(q_engine)
  q_engine.vector_store = qe_vector_store.vector_store_type
  q_engine.save()

  # build document index
  try:
    docs_processed, docs_not_processed = \
        build_doc_index(doc_url, query_engine, qe_vector_store)
  except Exception as e:
    # delete query engine model if build unsuccessful
    QueryDocument.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()
    QueryDocumentChunk.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()
    QueryEngine.delete_by_id(q_engine.id)
    raise InternalServerError(str(e)) from e

  Logger.info(f"Completed query engine build for {query_engine}")

  return q_engine, docs_processed, docs_not_processed


def build_doc_index(doc_url: str, query_engine: str,
                    qe_vector_store: VectorStore) -> \
        Tuple[List[QueryDocument], List[str]]:
  """
  Build the document index.
  Supports GCS URLs and http(s)://, containing PDF files, text
  files, html, csv.

  Args:
    doc_url: URL pointing to folder of documents
    query_engine: the query engine to build the index for

  Returns:
    Tuple of list of QueryDocument objects of docs processed,
      list of urls of docs not processed
  """
  q_engine = QueryEngine.find_by_name(query_engine)
  if q_engine is None:
    raise ResourceNotFoundException(f"cant find query engine {query_engine}")

  storage_client = storage.Client(project=PROJECT_ID)

  # initialize the vector store index
  qe_vector_store.init_index()

  try:
    # process docs at url and upload embeddings to vector store
    docs_processed, docs_not_processed = process_documents(
      doc_url, qe_vector_store, q_engine, storage_client)

    # make sure we actually processed some docs
    if len(docs_processed) == 0:
      raise NoDocumentsIndexedException(
          f"Failed to process any documents at url {doc_url}")

    # deploy vectore store (e.g. create endpoint for matching engine)
    # db vector stores typically don't require this step.
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
  # get datasource class for doc_url
  data_source = datasource_from_url(doc_url, storage_client)

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

      # generate embedding data and store in vector store
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
        clean_text = html_to_text(text_chunks[i])
        sentences = html_to_sentence_list(text_chunks[i])
        query_doc_chunk = QueryDocumentChunk(
                              query_engine_id=q_engine.id,
                              query_document_id=query_doc.id,
                              index=i+index_base,
                              text=text_chunks[i],
                              clean_text=clean_text,
                              sentences=sentences)
        query_doc_chunk.save()

      index_base = new_index_base
      docs_processed.append(query_doc)

  return docs_processed, data_source.docs_not_processed


def vector_store_from_query_engine(q_engine: QueryEngine) -> VectorStore:
  qe_vector_store_type = q_engine.vector_store
  if qe_vector_store_type is None:
    # set to default vector store
    qe_vector_store_type = DEFAULT_VECTOR_STORE

  qe_vector_store_class = VECTOR_STORES.get(qe_vector_store_type)
  if qe_vector_store_class is None:
    raise InternalServerError(
       f"vector store class {qe_vector_store_type} not found in config")

  qe_vector_store = qe_vector_store_class(q_engine, q_engine.embedding_type)
  return qe_vector_store


def datasource_from_url(doc_url, storage_client):
  """
  Check if doc_url is supported as a data source.  If so return
  a DataSource class to handle the url.
  If not raise an InternalServerError exception.
  """
  if doc_url.startswith("gs://"):
    return DataSource(storage_client)
  elif doc_url.startswith("http://") or doc_url.startswith("https://"):
    return WebDataSource(storage_client)
  else:
    raise InternalServerError(
        f"No datasource available for doc url [{doc_url}]")
