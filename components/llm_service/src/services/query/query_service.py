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
from copy import deepcopy
import tempfile
import traceback
import os
import json
from numpy.linalg import norm
import numpy as np
import pandas as pd
from typing import List, Optional, Tuple, Dict
from google.cloud import storage
from rerankers import Reranker
from common.utils.logging_handler import Logger
from common.models import (UserQuery, QueryResult, QueryEngine,
                           QueryDocument,
                           QueryReference, QueryDocumentChunk,
                           BatchJobModel)
from common.models.llm_query import (QE_TYPE_VERTEX_SEARCH,
                                     QE_TYPE_LLM_SERVICE,
                                     QE_TYPE_INTEGRATED_SEARCH,
                                     QUERY_AI_RESPONSE)
from common.utils.auth_service import create_authz_filter
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError,
                                 UnauthorizedUserError)
from common.utils.http_exceptions import InternalServerError
from services import embeddings
from services.llm_generate import (get_context_prompt,
                                   llm_chat,
                                   check_context_length)
from services.query.query_prompts import (get_question_prompt,
                                          get_summarize_prompt)
from services.query.vector_store import (VectorStore,
                                         MatchingEngineVectorStore,
                                         PostgresVectorStore,
                                         NUM_MATCH_RESULTS)
from services.query.data_source import DataSource
from services.query.web_datasource import WebDataSource
from services.query.sharepoint_datasource import SharePointDataSource
from services.query.vertex_search import (build_vertex_search,
                                          query_vertex_search,
                                          delete_vertex_search)
from utils.errors import (NoDocumentsIndexedException,
                          ContextWindowExceededException)
from utils.file_helper import validate_multimodal_file_type
from utils import text_helper
from config import (PROJECT_ID, DEFAULT_QUERY_CHAT_MODEL,
                    DEFAULT_MULTIMODAL_LLM_TYPE,
                    DEFAULT_QUERY_EMBEDDING_MODEL,
                    DEFAULT_QUERY_MULTIMODAL_EMBEDDING_MODEL,
                    DEFAULT_WEB_DEPTH_LIMIT, get_model_config,
                    MODALITY_SET)
from config.vector_store_config import (DEFAULT_VECTOR_STORE,
                                        VECTOR_STORE_LANGCHAIN_PGVECTOR,
                                        VECTOR_STORE_MATCHING_ENGINE)

# pylint: disable=broad-exception-caught,ungrouped-imports

Logger = Logger.get_logger(__file__)

VECTOR_STORES = {
  VECTOR_STORE_MATCHING_ENGINE: MatchingEngineVectorStore,
  VECTOR_STORE_LANGCHAIN_PGVECTOR: PostgresVectorStore
}

RERANK_MODEL_NAME = "colbert"
reranker = Reranker(RERANK_MODEL_NAME, verbose=0)

# minimum number of references to return
MIN_QUERY_REFERENCES = 2
# total number of references to return from integrated search
NUM_INTEGRATED_QUERY_REFERENCES = 6


async def query_generate(
            user_id: str,
            prompt: str,
            q_engine: QueryEngine,
            user_data: Optional[dict] = None,
            llm_type: Optional[str] = None,
            user_query: Optional[UserQuery] = None,
            rank_sentences=False,
            query_filter: Optional[dict]=None) -> \
                Tuple[QueryResult, List[QueryReference]]:
  """
  Execute a query over a query engine and generate a response.

  The rule for determining the model used for question generation is:
    if llm_type is passed as an arg use it
    else if llm_type is set in query engine use that
    else use the default query chat model

  Args:
    user_id: user id of user making query
    prompt: the text prompt to pass to the query engine
    q_engine: the name of the query engine to use
    user_data (optional): dict of user data from auth token
    llm_type (optional): chat model to use for query
    user_query (optional): an existing user query for context
    rank_sentences: (optional): rank sentences in retrieved chunks
    query_filter: (optional): dict of key value pairs for filtering results

  Returns:
    QueryResult object,
    list of QueryReference objects (see query_search)

  Raises:
    ResourceNotFoundException if the named query engine doesn't exist
  """
  Logger.info(f"Executing query: "
              f"llm_type=[{llm_type}], "
              f"user_id=[{user_id}], "
              f"prompt=[{prompt}], q_engine=[{q_engine.name}], "
              f"user_query=[{user_query}]")

  # process query filter and RBAC roles for user
  authz_filter = create_authz_filter(user_data)
  Logger.info(f"query_generate authz_filter = {authz_filter}")

  if query_filter is not None:
    query_filter = json.loads(query_filter)
  else:
    query_filter = {}

  if authz_filter:
    query_filter.update(authz_filter)

  if not query_filter:
    query_filter = None
  Logger.info(f"query_generate query filter = {query_filter}")

  # determine question generation model
  if llm_type is None:
    if q_engine.llm_type is not None:
      llm_type = q_engine.llm_type
    else:
      llm_type = DEFAULT_QUERY_CHAT_MODEL
  Logger.info(f"query_generate {llm_type=}")

  # check if user has access to model
  if not get_model_config().is_model_enabled_for_user(llm_type, user_data):
    raise UnauthorizedUserError("User does not have access to model")

  # perform retrieval
  query_references = await retrieve_references(prompt,
                                               q_engine,
                                               user_id,
                                               rank_sentences,
                                               query_filter)

  # Rerank references. Only need to do this if performing integrated search
  # from multiple child engines.
  if q_engine.query_engine_type == QE_TYPE_INTEGRATED_SEARCH and \
      len(query_references) > 1:
    query_references = rerank_references(prompt, query_references)

  # Update user query with ranked references. We do this before generating
  # the answer so the frontend can display the retrieved results as soon as
  # they are available.
  if user_query:
    update_user_query(
        prompt, None, user_id, q_engine, query_references, user_query)

  # generate question prompt
  # (from user's text prompt plus text info in query_references)
  question_prompt, query_references = \
      await generate_question_prompt(prompt,
                                     llm_type,
                                     query_references,
                                     user_query)

  # generate list of URLs for additional context
  # (from non-text info in query_references)
  context_urls = []
  context_urls_mimetype = []
  for ref in query_references:
    if hasattr(ref, "modality") and ref.modality != "text":
      if hasattr(ref, "chunk_url"):
        ref_filename = ref.chunk_url
        ref_mimetype = validate_multimodal_file_type(file_name=ref_filename,
                                                     file_b64=None)
        context_urls.append(ref_filename)
        context_urls_mimetype.append(ref_mimetype)
        # TODO: If ref is a video chunk, then update ref.chunk_url
        # according to ref.timestamp_start and ref.timestamp_stop

  # send prompt and additional context to model
  question_response = await llm_chat(question_prompt, llm_type,
                                     chat_file_types=context_urls_mimetype,
                                     chat_file_urls=context_urls)

  # update user query with response
  if user_query:
    # insert the response before the just added references
    user_query.history.insert(
        len(user_query.history) - 1, {QUERY_AI_RESPONSE: question_response})
    user_query.save(merge=True)
    Logger.info(f"SC241001: {user_query.history=}")

  # save query result
  query_ref_ids = [ref.id for ref in query_references]
  query_result = QueryResult(query_engine_id=q_engine.id,
                             query_engine=q_engine.name,
                             query_refs=query_ref_ids,
                             prompt=prompt,
                             response=question_response)
  query_result.save()

  return query_result, query_references

async def generate_question_prompt(prompt: str,
                                   llm_type: str,
                                   query_references: List[QueryReference],
                                   user_query=None) -> \
                                   Tuple[str, QueryReference]:
  """
  Generate question prompt for RAG, given initial prompt and retrieved
  references.  If necessary, trim context or references to fit context window
  of generation model.

  Args:
    prompt: the original user prompt
    llm_type: chat model to use for generation
    query_references: list of retrieved query references
    user_query (optional): existing user query for context

  Returns:
    question prompt (str)
    list of QueryReference objects

  Raises:
    ContextWindowExceededException if the model context window is exceeded
  """
  # incorporate user query context in prompt if it exists
  chat_history = ""
  if user_query is not None:
    chat_history = get_context_prompt(user_query=user_query)

  # generate default prompt
  question_prompt = get_question_prompt(
    prompt, chat_history, query_references, llm_type)

  # check prompt against context length of generation model
  try:
    check_context_length(question_prompt, llm_type)
  except ContextWindowExceededException:
    # first try popping reference results
    while len(query_references) > MIN_QUERY_REFERENCES:
      q_ref = query_references.pop()
      Logger.info(f"Dropped reference {q_ref.id}")
      question_prompt = get_question_prompt(
        prompt, chat_history, query_references, llm_type
      )
      try:
        check_context_length(question_prompt, llm_type)
        break
      except ContextWindowExceededException:
        pass
    # check again
    try:
      check_context_length(question_prompt, llm_type)
    except ContextWindowExceededException:
      # summarize chat history
      chat_history = await summarize_history(chat_history, llm_type)
      question_prompt = get_question_prompt(
        prompt, chat_history, query_references, llm_type
      )
      # exception will be propagated if context is too long at this point
      check_context_length(question_prompt, llm_type)

  return question_prompt, query_references

async def summarize_history(chat_history: str,
                            llm_type: str) -> str:
  """
  Use an LLM to summarize a chat history.

  Args:
    chat_history: string of previous chat
    llm_type: model to use to perform the summaries
  Returns:
    summarized chat history
  """
  summarize_prompt = get_summarize_prompt(chat_history)
  summary = await llm_chat(summarize_prompt, llm_type)
  Logger.info(f"generated summary with LLM {llm_type}: {summary}")
  return summary

async def retrieve_references(prompt: str,
                              q_engine: QueryEngine,
                              user_id: str,
                              rank_sentences: bool = False,
                              query_filter: dict = None)-> List[QueryReference]:
  """
  Execute a query over a query engine and retrieve reference documents.

  Args:
    prompt: the text prompt to pass to the query engine
    q_engine: the name of the query engine to use
    user_id: user id of user making query
    rank_sentences (bool): rank sentence relevance in retrieved chunks
  Returns:
    list of QueryReference objects
  """
  # perform retrieval for prompt
  query_references = []

  if q_engine.query_engine_type == QE_TYPE_VERTEX_SEARCH:
    query_references = \
         await query_vertex_search(q_engine, prompt,
                                   NUM_MATCH_RESULTS, query_filter)
  elif q_engine.query_engine_type == QE_TYPE_INTEGRATED_SEARCH:
    child_engines = QueryEngine.find_children(q_engine)
    for child_engine in child_engines:
      # make a recursive call to retrieve references for child engine
      child_query_references = await retrieve_references(prompt,
                                                         child_engine,
                                                         user_id,
                                                         query_filter)
      query_references += child_query_references
  elif q_engine.query_engine_type == QE_TYPE_LLM_SERVICE or \
      not q_engine.query_engine_type:
    # default if type is not set to llm service query
    query_references = await query_search(q_engine, prompt,
                                          rank_sentences, query_filter)

  return query_references

async def query_search(q_engine: QueryEngine,
                       query_prompt: str,
                       rank_sentences: bool = False,
                       query_filter: dict = None) -> List[QueryReference]:
  """
  For a query prompt, retrieve text chunks with doc references
  from matching documents.

  Args:
    q_engine: QueryEngine to search
    query_prompt (str):  user query
    rank_sentences: rank sentence relevance in retrieved chunks

  Returns:
    list of QueryReference models

  """
  # Get is_multimodal flag from q_engine
  params = q_engine.params #q_engine should always have a field called params
  is_multimodal = False
  if "is_multimodal" in params and isinstance(params["is_multimodal"], str):
    is_multimodal = params["is_multimodal"].lower()
    is_multimodal = is_multimodal == "true"

  Logger.info(f"Retrieving doc references for q_engine=[{q_engine.name}], "
              f"query_prompt=[{query_prompt}]")
  # generate embeddings for prompt
  if is_multimodal:
    # TODO: Once multimodal embedding model can operate in batch mode
    # and get_multimodal_embeddings is edited to send multiple chunks to
    # the model in batch mode, then edit this code so that we input a
    # LIST of text strings and a LIST of images to get_multimodal_embeddings
    # instead of a single text string and a single image. Then also
    # extract a single embedding vector from the output instead
    # of a LIST of embedding vectors.
    # TODO: Once we allow multimodal queries, input an image or video
    # potentially audio into get_multimodal_embeddings, instead of None,
    # and set "image" or "video" or potentially "audio" keys of query_embedding
    query_embeddings = \
      await embeddings.get_multimodal_embeddings(query_prompt,
                                            None,
                                            q_engine.embedding_type)
    query_embedding = query_embeddings["text"]
  else:
    # The text-only embedding model operates in batch mode
    # and get_embeddings sends multiple chunks to
    # the model in batch mode, and so we input a
    # LIST of text strings to get_embeddings
    # instead of a single text string.  Then we
    # extract a single embedding vector from the output instead
    # of a LIST of embedding vectors.
    _, query_embeddings = \
        await embeddings.get_embeddings([query_prompt],
                                        q_engine.embedding_type)
    query_embedding = query_embeddings[0]

  # retrieve indexes of relevant document chunks from vector store
  qe_vector_store = vector_store_from_query_engine(q_engine)
  match_indexes_list = qe_vector_store.similarity_search(q_engine,
                                                         query_embedding,
                                                         query_filter)

  query_references = []
  # Assemble document chunk models from vector store indexes
  for match in match_indexes_list:
    doc_chunk = QueryDocumentChunk.find_by_index(q_engine.id, match)
    if doc_chunk is None:
      raise ResourceNotFoundException(
        f"Missing doc chunk match index {match} q_engine {q_engine.name}")

    query_doc = QueryDocument.find_by_id(doc_chunk.query_document_id)
    if query_doc is None:
      raise ResourceNotFoundException(
        f"Query doc {doc_chunk.query_document_id} q_engine {q_engine.name}")

    query_reference = make_query_reference(q_engine=q_engine,
                                           query_doc=query_doc,
                                           doc_chunk=doc_chunk,
                                           query_embeddings=query_embeddings,
                                           rank_sentences=rank_sentences)
    query_reference.save()
    query_references.append(query_reference)

  Logger.info(f"Retrieved {len(query_references)} "
               f"references={query_references}")

  return query_references


# Create a single QueryReference object
def make_query_reference(q_engine: QueryEngine,
                           query_doc: QueryDocument,
                           doc_chunk: QueryDocumentChunk,
                           query_embeddings: List[Optional[List[float]]],
                           rank_sentences: bool = False) -> \
                            QueryReference:
  """
  Make a single QueryReference object, with appropriate fields
  for modality
  
  Args:
    q_engine: The QueryEngine object that was searched
    query_doc: The QueryDocument object retreived from q_engine
    doc_chunk: The QueryDocumentChunk object of the retrieved query_doc
    query_embeddings: The embedding vector for the query prompt
    
  Returns:
    query_reference: The QueryReference object corresponding to doc_chunk
  """
  # Get modality of document chunk, make lowercase
  # If modality is None, set it equal to default value "text"
  modality = doc_chunk.modality
  if modality is None:
    modality = "text"
  modality = modality.casefold()

  # Clean up text chunk
  if modality=="text":

    # Clean up text in document chunk.
    clean_text = doc_chunk.clean_text
    if not clean_text:
      clean_text = text_helper.clean_text(doc_chunk.text)

    # Pick out sentences from document chunk and rank them.
    if rank_sentences:
      # Assemble sentences from a document chunk. Currently it gets the
      # sentences from the top-ranked document chunk.
      sentences = doc_chunk.sentences
      if not sentences or len(sentences) == 0:
        sentences = text_helper.text_to_sentence_list(doc_chunk.text)

      # Only update clean_text when sentences is not empty.
      Logger.info(f"Processing {len(sentences)} sentences.")
      if sentences and len(sentences) > 0:
        top_sentences = get_top_relevant_sentences(
            q_engine, query_embeddings, sentences,
            expand_neighbors=2, highlight_top_sentence=True)
        clean_text = " ".join(top_sentences)

  # Clean up image chunk
  elif modality=="image":
    # TODO: Placeholder to fill with actual logic
    pass

  # Clean up video chunk
  elif modality=="video":
    # TODO: Placeholder to fill with actual logic
    pass

  # Clean up audio chunk
  elif modality=="audio":
    # TODO: Placeholder to fill with actual logic
    pass

  # Create dict to hold all fields of query_reference,
  # depending on its modality
  query_reference_dict = {}
  # For chunk of any modality
  query_reference_dict["query_engine_id"]=q_engine.id
  query_reference_dict["query_engine"]=q_engine.name
  query_reference_dict["document_id"]=query_doc.id
  query_reference_dict["document_url"]=query_doc.doc_url
  query_reference_dict["modality"]=modality
  query_reference_dict["chunk_id"]=doc_chunk.id
  # For text chunk only
  if modality=="text":
    query_reference_dict["page"]=doc_chunk.page
    query_reference_dict["document_text"]=clean_text
  # For image chunk only
  elif modality=="image":
    query_reference_dict["page"]=doc_chunk.page
    query_reference_dict["chunk_url"]=doc_chunk.chunk_url
  # For video and audio chunks only
  elif modality in {"video", "audio"}:
    query_reference_dict["chunk_url"]=doc_chunk.chunk_url
    query_reference_dict["timestamp_start"]=doc_chunk.timestamp_start
    query_reference_dict["timestamp_stop"]=doc_chunk.timestamp_stop

  # Create query_reference out of dict
  query_reference = QueryReference.from_dict(query_reference_dict)

  # Return query_reference
  return query_reference


def rerank_references(prompt: str,
                      query_references: List[QueryReference]) -> \
                        List[QueryReference]:
  """
  Return a list of QueryReferences ranked by relevance to the prompt.

  Args:
    prompt: the text prompt to pass to the query engine
    query_references: list of QueryReference objects (possibly
                      from multiple q_engines)
  Returns:
    list of QueryReference objects
  """

  Logger.info(f"Reranking {len(query_references)} references for "
              f"query_prompt=[{prompt}]")

  # reranker function requires text and ids as separate params
  query_ref_text = []
  query_ref_ids = []
  query_ref_lookup = {}

  for query_ref in query_references:
    Logger.info(f"Query ref {query_ref.id}, {query_ref.chunk_id}")
    query_ref_text.append(query_ref.document_text)
    query_ref_ids.append(query_ref.id)
    query_ref_lookup[query_ref.id] = query_ref

  # rerank, passing in QueryReference ids
  ranked_results = reranker.rank(
    query=prompt,
    docs=query_ref_text,
    doc_ids=query_ref_ids)
  ranked_results = ranked_results.top_k(NUM_INTEGRATED_QUERY_REFERENCES)

  # order the original references based on the rank
  ranked_query_refs = []
  ranked_query_ref_ids = [r.doc_id for r in ranked_results]
  for i in ranked_query_ref_ids:
    ranked_query_refs.append(query_ref_lookup[i])

  return ranked_query_refs

def get_top_relevant_sentences(q_engine, query_embeddings,
    sentences, expand_neighbors=2, highlight_top_sentence=False) -> list:

  _, sentence_embeddings = embeddings.get_embeddings(sentences,
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
  for _, row in sentence_df.iterrows():
    x = row
    y = query_df
    # calculate the cosine similarity
    cosine = np.dot(x, y) / (norm(x) * norm(y))
    cos_sim.append(cosine[0])

  return cos_sim

async def batch_query_generate(request_body: Dict, job: BatchJobModel) -> Dict:
  """
  Handle a batch job request for query generation.

  Args:
    request_body: dict of query params
    job: BatchJobModel model object
  Returns:
    dict containing job meta data
  """
  query_engine_id = request_body.get("query_engine_id")
  prompt = request_body.get("prompt")
  user_id = request_body.get("user_id")
  user_query_id = request_body.get("user_query_id", None)
  llm_type = request_body.get("llm_type")
  rank_sentences = request_body.get("rank_sentences", None)

  q_engine = QueryEngine.find_by_id(query_engine_id)
  if q_engine is None:
    raise ResourceNotFoundException(f"Query Engine id {query_engine_id}")

  user_query = None
  if user_query_id:
    user_query = UserQuery.find_by_id(user_query_id)
    if user_query is None:
      raise ResourceNotFoundException(f"UserQuery id {user_query_id}")

  Logger.info(f"Starting batch job for query on [{q_engine.name}] "
              f"job id [{job.id}], request_body=[{request_body}]")

  query_result, query_references = await query_generate(
      user_id, prompt, q_engine, llm_type, user_query, rank_sentences)

  # update user query
  user_query, query_reference_dicts = \
      update_user_query(prompt,
                        query_result.response,
                        user_id,
                        q_engine,
                        query_references,
                        user_query)

  # update result data in batch job model
  result_data = {
    "query_engine_id": q_engine.id,
    "query_result_id": query_result.id,
    "user_query_id": user_query.id,
    "query_references": query_reference_dicts
  }
  job.result_data = result_data
  job.save(merge=True)

  Logger.info(f"Completed batch job query execute for {q_engine.name}")

  return result_data

def update_user_query(prompt: str,
                      response: str,
                      user_id: str,
                      q_engine: QueryEngine,
                      query_references: List[QueryReference],
                      user_query: UserQuery = None,
                      query_filter=None) -> \
                      Tuple[UserQuery, dict]:
  """ Save user query history """
  #SC240930: Should the second output be a LIST of dicts? The dicts version of query_references,
  #SC240930: which is a LIST of QueryReference objects?
  query_reference_dicts = [
    ref.get_fields(reformat_datetime=True) for ref in query_references
  ]

  # create user query if needed
  if user_query is None:
    user_query = UserQuery(user_id=user_id,
                          query_engine_id=q_engine.id,
                          prompt=prompt)
    user_query.save()
  user_query.update_history(prompt=prompt,
                            response=response,
                            references=query_reference_dicts)

  if query_filter:
    user_query.update_history(custom_entry={
      "query_filter": query_filter,
    })

  return user_query, query_reference_dicts

async def batch_build_query_engine(request_body: Dict,
                                   job: BatchJobModel) -> Dict:
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
  description = request_body.get("description")
  user_id = request_body.get("user_id")
  query_engine_type = request_body.get("query_engine_type")
  llm_type = request_body.get("llm_type")
  embedding_type = request_body.get("embedding_type")
  vector_store_type = request_body.get("vector_store")
  params = request_body.get("params")

  Logger.info(f"Starting batch job for query engine [{query_engine}] "
              f"job id [{job.id}], request_body=[{request_body}]")
  Logger.info(f"doc_url: [{doc_url}] user id: [{user_id}]")
  Logger.info(f"query engine type: [{query_engine_type}]")
  Logger.info(f"query description: [{description}]")
  Logger.info(f"llm type: [{llm_type}]")
  Logger.info(f"embedding type: [{embedding_type}]")
  Logger.info(f"vector store type: [{vector_store_type}]")
  Logger.info(f"params: [{params}]")

  q_engine, docs_processed, docs_not_processed = \
      await query_engine_build(doc_url, query_engine, user_id,
                               query_engine_type,
                               llm_type, description,
                               embedding_type, vector_store_type, params)

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

async def query_engine_build(doc_url: str,
                             query_engine: str,
                             user_id: str,
                             query_engine_type: Optional[str] = None,
                             llm_type: Optional[str] = None,
                             query_description: Optional[str] = None,
                             embedding_type: Optional[str] = None,
                             vector_store_type: Optional[str] = None,
                             params: Optional[dict] = None
                             ) -> Tuple[str, List[QueryDocument], List[str]]:
  """
  Build a new query engine.

  Args:
    doc_url: the URL to the set of documents to be indexed
    query_engine: the name of the query engine to create
    user_id: user id of engine creator
    query_engine_type: type of query engine to build
    llm_type: llm used for query answer generation
    embedding_type: LLM used for query embeddings
    query_description: description of the query engine
    vector_store_type: vector store type (from config.vector_store_config)
    params: query engine build params

  Returns:
    Tuple of QueryEngine id, list of QueryDocument objects of docs processed,
      list of urls of docs not processed

  Raises:
    ValidationError if the named query engine already exists
  """
  q_engine = QueryEngine.find_by_name(query_engine)
  if q_engine is not None:
    raise ValidationError(f"Query engine {query_engine} already exists")

  # process special build params
  params = params or {}

  is_multimodal = False
  if "is_multimodal" in params and isinstance(params["is_multimodal"], str):
    is_multimodal = params["is_multimodal"].lower()
    is_multimodal = is_multimodal == "true"

  is_public = True
  if "is_public" in params and isinstance(params["is_public"], str):
    is_public = params["is_public"].lower()
    is_public = is_public == "true"

  associated_agents = []
  if "agents" in params and isinstance(params["agents"], str):
    associated_agents = params["agents"].split(",")
    associated_agents = [qe.strip() for qe in associated_agents]

  associated_query_engines = []
  if "associated_engines" in params:
    associated_qe_names = params["associated_engines"].split(",")
    associated_query_engines = [
      QueryEngine.find_by_name(qe_name.strip())
      for qe_name in associated_qe_names
    ]

  manifest_url = None
  if "manifest_url" in params:
    manifest_url = params["manifest_url"]

  # create model
  if llm_type is None:
    if is_multimodal:
      llm_type = DEFAULT_MULTIMODAL_LLM_TYPE
    else:
      llm_type = DEFAULT_QUERY_CHAT_MODEL

  if embedding_type is None:
    if is_multimodal:
      embedding_type = DEFAULT_QUERY_MULTIMODAL_EMBEDDING_MODEL
    else:
      embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL

  if not query_engine_type:
    query_engine_type = QE_TYPE_LLM_SERVICE

  if query_engine_type in (QE_TYPE_VERTEX_SEARCH,
                           QE_TYPE_INTEGRATED_SEARCH):
    # no vector store set for vertex search or integrated search
    vector_store_type = None

  # create query engine model
  q_engine = QueryEngine(name=query_engine,
                         created_by=user_id,
                         query_engine_type=query_engine_type,
                         llm_type=llm_type,
                         description=query_description,
                         embedding_type=embedding_type,
                         vector_store=vector_store_type,
                         is_public=is_public,
                         doc_url=doc_url,
                         manifest_url=manifest_url,
                         agents=associated_agents,
                         params=params)

  q_engine.save()

  # build document index
  docs_processed = []
  docs_not_processed = []

  try:
    if query_engine_type == QE_TYPE_VERTEX_SEARCH:
      docs_processed, docs_not_processed = build_vertex_search(q_engine)

    elif query_engine_type == QE_TYPE_LLM_SERVICE:
      # retrieve vector store class and store type in q_engine
      qe_vector_store = vector_store_from_query_engine(q_engine)
      q_engine.vector_store = qe_vector_store.vector_store_type
      q_engine.update()

      docs_processed, docs_not_processed = \
          await build_doc_index(doc_url,
                                q_engine,
                                qe_vector_store,
                                is_multimodal)

    elif query_engine_type == QE_TYPE_INTEGRATED_SEARCH:
      # for each associated query engine store the current engine as its parent
      for aq_engine in associated_query_engines:
        aq_engine.parent_engine_id = q_engine.id
        aq_engine.update()

    else:
      raise RuntimeError(f"Invalid query_engine_type {query_engine_type}")
  except Exception as e:
    # delete query engine models if build unsuccessful
    delete_engine(q_engine, hard_delete=True)
    raise InternalServerError(str(e)) from e

  Logger.info(f"Completed query engine build for {query_engine}")

  return q_engine, docs_processed, docs_not_processed

async def build_doc_index(doc_url: str, q_engine: QueryEngine,
                    qe_vector_store: VectorStore,
                    is_multimodal: Optional[bool]=False) -> \
        Tuple[List[QueryDocument], List[str]]:
  """
  Build the document index.
  Supports GCS URLs and http(s)://, containing PDF files, text
  files, html, csv.

  Args:
    doc_url: URL pointing to folder of documents
    q_engine: the query engine name to build the index for
    qe_vector_store: the vector store used for the query engine
    is_multimodal: True if multimodal, False if text-only (default False)

  Returns:
    Tuple of list of QueryDocument objects of docs processed,
      list of uris of docs not processed
  """
  storage_client = storage.Client(project=PROJECT_ID)

  # initialize the vector store index
  qe_vector_store.init_index()

  try:
    # process docs at url and upload embeddings to vector store
    docs_processed, docs_not_processed = await process_documents(
      doc_url, qe_vector_store, q_engine, storage_client, is_multimodal)

    # make sure we actually processed some docs
    if len(docs_processed) == 0:
      raise NoDocumentsIndexedException(
          f"Failed to process any documents at url {doc_url}")

    # deploy vector store (e.g. create endpoint for matching engine)
    # db vector stores typically don't require this step.
    qe_vector_store.deploy()

    return docs_processed, docs_not_processed

  except Exception as e:
    Logger.error(f"Error creating doc index {e}")
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

async def process_documents(doc_url: str, qe_vector_store: VectorStore,
                      q_engine: QueryEngine, storage_client,
                      is_multimodal: Optional[bool] = False) -> \
                      Tuple[List[QueryDocument], List[str]]:
  """
  Process docs in data source and upload embeddings to vector store
  
  Args:
    doc_url: URL pointing to folder of documents
    qe_vector_store: the vector store used for the query engine
    q_engine: the query engine name to build the index for
    storage_client: client used for storing the data source
    is_multimodal: True if multimodal, False if text-only (default False)
  
  Returns:
     Tuple of list of QueryDocument objects for docs processed,
        list of doc urls of docs not processed
  """
  # get datasource class for doc_url
  data_source = datasource_from_url(doc_url, q_engine, storage_client)

  # initialize metadata
  metadata_manifest = data_source.init_metadata(q_engine)

  docs_processed = []
  with tempfile.TemporaryDirectory() as temp_dir:
    data_source_files = data_source.download_documents(doc_url, temp_dir)

    # counter for unique index ids
    index_base = 0

    for data_source_file in data_source_files:
      doc_name = data_source_file.doc_name
      index_doc_url = data_source_file.src_url
      doc_filepath = data_source_file.local_path

      Logger.info(f"processing [{doc_name}] with {is_multimodal=}")

      if is_multimodal:
        doc_chunks = data_source.chunk_document_multimodal(doc_name,
                                                      index_doc_url,
                                                      doc_filepath)
      else:
        #chunk_document returns 2 outputs, text_chunks and embed_chunks.
        #Each element of text_chunks has the same info as its corresponding
        #element in embed_chunks, but is padded with adjacent sentences
        #before and after. Use the 2nd output here (embed_chunks).
        _, doc_chunks = data_source.chunk_document(doc_name,
                                                   index_doc_url,
                                                   doc_filepath)

      if doc_chunks is None or len(doc_chunks) == 0:
        # unable to process this doc; skip
        Logger.error(f"unable to chunk doc [{index_doc_url}]")
        continue

      Logger.info(f"doc chunks extracted for [{doc_name}]")

      # generate embedding data and store in vector store
      try:
        metadata = metadata_manifest.get(doc_name, None)
        metadata_list = []
        if metadata is not None:
          metadata_list = [deepcopy(metadata) for chunk in doc_chunks]
        if is_multimodal:
          new_index_base = \
            await qe_vector_store.index_document_multimodal(doc_name,
                                                       doc_chunks,
                                                       index_base)
          Logger.info(
            f"Successfully indexed {len(doc_chunks)} chunks for [{doc_name}]"
            )
        else:
          new_index_base = \
            await qe_vector_store.index_document(doc_name,
                                                 doc_chunks,
                                                 index_base,
                                                 metadata_list)
          Logger.info(
            f"Successfully indexed {len(doc_chunks)} chunks for [{doc_name}]"
            )
      except Exception as e:
        # unable to process this doc; skip
        Logger.error(f"error indexing doc [{index_doc_url}]: {str(e)}")
        data_source.docs_not_processed.append(index_doc_url)
        continue

      # cleanup temp local file
      os.remove(doc_filepath)

      # store QueryDocument and QueryDocumentChunk models
      query_doc = QueryDocument(query_engine_id=q_engine.id,
                                query_engine=q_engine.name,
                                doc_url=index_doc_url,
                                index_file=data_source_file.doc_id,
                                index_start=index_base,
                                index_end=new_index_base,
                                metadata=metadata)
      query_doc.save()

      # Initialize counter of all ORM objects to be made from all chunks
      j = 0
      # Iterate over all chunks
      for i in range(0, len(doc_chunks)):

        if is_multimodal:
          # Use multimodal pipeline

          # Initialize list of ORM object indexes and ids to be made
          # from this chunk
          linked_indexes = []
          linked_ids = []
          # Sort keys of ith chunk in alphabetical order
          # Keys of interest are in MODALITY_SET
          # These keys hold info related to specific modalities that
          # need to be stored in ORM objects
          sorted_keys = sorted(list(doc_chunks[i].keys()))

          # Create a QueryDocumentChunk ORM object for each modality
          # of ith chunk, in alphabetical order
          for key in sorted_keys:
            if key in MODALITY_SET:
              # doc_chunk is dict representing ith chunk
              doc_chunk = doc_chunks[i]
              # Make ORM object for current modality of ith chunk
              query_doc_chunk = make_query_document_chunk(
                query_engine_id=q_engine.id,
                query_document_id=query_doc.id,
                index=j+index_base,
                doc_chunk=doc_chunk,
                page=i,
                data_source=data_source,
                modality=key)
              # Save ORM object in Firestore
              query_doc_chunk.save()
              # Build up lists of ORM object indexes and ids made for ith chunk
              linked_indexes.append(query_doc_chunk.index)
              linked_ids.append(query_doc_chunk.id)
              # Increment counter of all ORM objects made for all chunks
              j+=1

          # Set linked_ids field of all ORM objects just made for ith chunk
          for index in linked_indexes:
            query_doc_chunk = \
              QueryDocumentChunk.find_by_index(q_engine.id, index)
            query_doc_chunk.linked_ids = linked_ids

        else:
          # Use text-only pipeline

          # doc_chunk is a dict representing the ith chunk
          # with key "text"
          doc_chunk = {}
          doc_chunk["text"] = doc_chunks[i]
          # Make ORM object for text modality of ith chunk
          query_doc_chunk = make_query_document_chunk(
            query_engine_id=q_engine.id,
            query_document_id=query_doc.id,
            index=i+index_base,
            doc_chunk=doc_chunk,
            page=None,
            data_source=data_source,
            modality="text")
          # Save ORM object in Firestore
          query_doc_chunk.save()

      if is_multimodal:
        Logger.info(f"{j} doc chunk models created for [{doc_name}]")
      else:
        Logger.info(f"{i+1} doc chunk models created for [{doc_name}]")

      index_base = new_index_base
      docs_processed.append(query_doc)

  return docs_processed, data_source.docs_not_processed

# Create a single QueryDocumentChunk object
def make_query_document_chunk(query_engine_id: str,
                              query_document_id: str,
                              index: int,
                              doc_chunk: dict,
                              page: int,
                              data_source: DataSource,
                              modality: str) -> \
                                QueryDocumentChunk:
  """
  Make a single QueryDocumentChunk object, with appropriate fields
  for modality
  
  Args:
    query_engine_id: The ID of the query engine
    query_document_id: The ID of the document that the doc_chunk came from
    index: The index assigned to the doc_chunk 
    doc_chunk: A dict representing the doc_chunk, with fields:
      "text": The text extracted from doc_chunk
      "image": The image bytes extracted from doc_chunk
    page: The page of the document that the doc_chunk came from
    data_source: The data source class of the document
    modality: The modality of the corresponding embedding vector 
      extracted from the doc_chunk
  
  Returns:
    query_document_chunk: QueryDocumentChunk object corresponding to doc_chunk
  """
  # Create dict to hold all fields of query_document_chunk,
  # depending on its modality
  query_document_chunk_dict = {}
  # For chunk of any modality
  query_document_chunk_dict["query_engine_id"]=query_engine_id
  query_document_chunk_dict["query_document_id"]=query_document_id
  query_document_chunk_dict["index"]=index
  query_document_chunk_dict["modality"]=modality
  # For text chunk only
  if modality=="text":
    query_document_chunk_dict["page"]=page
    query_document_chunk_dict["text"]=doc_chunk["text"]
    query_document_chunk_dict["clean_text"]=\
      data_source.clean_text(doc_chunk["text"])
    query_document_chunk_dict["sentences"]=\
      data_source.text_to_sentence_list(doc_chunk["text"])
  # For image chunk only
  elif modality=="image":
    query_document_chunk_dict["page"]=page
    if "image_url" in doc_chunk:
      query_document_chunk_dict["chunk_url"]=doc_chunk["image_url"]
  # For video and audio chunks only
  elif modality in {"video", "audio"}:
    #TODO: Insert logic to set values of the following keys:
    #  "chunk_url": Holds url to the file that the video/audio is saved to,
    #    if the video/audio chunk is saved to a separate file
    #  "timestamp_start": Holds timestamp of beginning of video/audio chunk
    #  "timestamp_stop": Holds timestamp of ending of video/audio chunk
    pass

  # Create query_document_chunk out of dict
  query_document_chunk = QueryDocumentChunk.from_dict(query_document_chunk_dict)

  # Return query_document_chunk
  return query_document_chunk


def vector_store_from_query_engine(q_engine: QueryEngine) -> VectorStore:
  """
  Retrieve Vector Store object for a Query Engine.

  A Query Engine is configured for the vector store it uses when it is
  built.  If there is no configured vector store the default is used.
  """
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

def datasource_from_url(doc_url: str,
                        q_engine: QueryEngine,
                        storage_client) -> DataSource:
  """
  Check if doc_url is supported as a data source.  If so return
  a DataSource class to handle the url.
  If not raise an InternalServerError exception.
  """
  if doc_url.startswith("gs://"):
    return DataSource(storage_client)
  elif doc_url.startswith("http://") or doc_url.startswith("https://"):
    params = q_engine.params or {}
    if "depth_limit" in params:
      depth_limit = params["depth_limit"]
    else:
      depth_limit = DEFAULT_WEB_DEPTH_LIMIT
    Logger.info(f"creating WebDataSource with depth limit [{depth_limit}]")
    # Create bucket name using query_engine name
    bucket_name = WebDataSource.downloads_bucket_name(q_engine.name)
    return WebDataSource(storage_client,
                         bucket_name=bucket_name,
                         depth_limit=depth_limit)
  elif doc_url.startswith("shpt://"):
    # Create bucket name using query_engine name
    bucket_name = SharePointDataSource.downloads_bucket_name(q_engine.name)
    return SharePointDataSource(storage_client,
                                bucket_name=bucket_name)
  else:
    raise InternalServerError(
        f"No datasource available for doc url [{doc_url}]")

def delete_engine(q_engine: QueryEngine, hard_delete=False):
  """
  Delete query engine and associated models and vector store data.
  """
  # delete vector store data
  try:
    if q_engine.query_engine_type == QE_TYPE_VERTEX_SEARCH:
      delete_vertex_search(q_engine)
    else:
      qe_vector_store = vector_store_from_query_engine(q_engine)
      qe_vector_store.delete()
  except Exception:
    # we make this error non-fatal as we want to delete the models
    Logger.error(
        f"error deleting vector store for query engine {q_engine.id}")
    Logger.error(traceback.print_exc())

  if hard_delete:
    Logger.info(f"performing hard delete of query engine {q_engine.id}")

    # delete query docs and chunks
    QueryDocument.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()

    QueryDocumentChunk.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()

    QueryReference.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()

    QueryResult.collection.filter(
      "query_engine_id", "==", q_engine.id
    ).delete()

    # delete query engine
    QueryEngine.delete_by_id(q_engine.id)
  else:
    Logger.info(f"performing soft delete of query engine {q_engine.id}")

    # delete query docs and chunks
    qdocs = QueryDocument.collection.filter(
      "query_engine_id", "==", q_engine.id).fetch()
    for qd in qdocs:
      qd.soft_delete_by_id(qd.id)

    qchunks = QueryDocumentChunk.collection.filter(
      "query_engine_id", "==", q_engine.id).fetch()
    for qc in qchunks:
      qc.soft_delete_by_id(qc.id)

    qrefs = QueryReference.collection.filter(
      "query_engine_id", "==", q_engine.id).fetch()
    for qr in qrefs:
      qr.soft_delete_by_id(qr.id)

    qres = QueryResult.collection.filter(
      "query_engine_id", "==", q_engine.id).fetch()
    for qr in qres:
      qr.soft_delete_by_id(qr.id)

    # delete query engine
    QueryEngine.soft_delete_by_id(q_engine.id)

  Logger.info(f"Successfully deleted q_engine=[{q_engine.name}]")
