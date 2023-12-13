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
Generate Query embeddings. Currently, using Vertex TextEmbedding model.
"""
import json
import time
from typing import List, Optional, Generator, Tuple
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from vertexai.preview.language_models import TextEmbeddingModel
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import post_method
from common.utils.token_handler import UserCredentials
from config import (GOOGLE_LLM, LANGCHAIN_LLM, DEFAULT_QUERY_EMBEDDING_MODEL,
                    LANGCHAIN_EMBEDDING_MODELS, VERTEX_EMBEDDING_MODELS,
                    LLM_SERVICE_EMBEDDING_MODELS, LLM_SERVICE_MODELS)
from langchain.schema.embeddings import Embeddings

# pylint: disable=broad-exception-caught

# Create a rate limit of 300 requests per minute.
API_CALLS_PER_SECOND = int(300 / 60)

# According to the docs, each request can process 5 instances per request
ITEMS_PER_REQUEST = 5

Logger = Logger.get_logger(__file__)

def get_embeddings(
    text_chunks: List[str], embedding_type: str = None) -> (
    Tuple)[List[bool], np.ndarray]:
  """
  Get embeddings for a list of text strings.

  Args:
    text_chunks: list of text chunks to generate embeddings for
    embedding_type: embedding type from config.EMBEDDING_MODELS
  Returns:
    Tuple of (list of booleans for chunk true if embeddings were generated,
              numpy array of embeddings indexed by chunks)
  """
  if embedding_type is None or embedding_type == "":
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL

  Logger.info(f"generating embeddings with {embedding_type}")

  is_successful, embeddings = _generate_embeddings_batched(
      embedding_type,
      text_chunks)

  return is_successful, embeddings

def _generate_embeddings_batched(embedding_type,
                                 text_chunks):
  embeddings_list: List[List[float]] = []

  # Prepare the batches using a generator
  batches = _generate_batches(text_chunks, ITEMS_PER_REQUEST)

  seconds_per_job = 1 / API_CALLS_PER_SECOND

  with ThreadPoolExecutor() as executor:
    futures = []
    for batch in batches:
      futures.append(
          executor.submit(generate_embeddings, batch, embedding_type)
      )
      time.sleep(seconds_per_job)

    for future in futures:
      embeddings_list.extend(future.result())

  is_successful = [
      embedding is not None for sentence, embedding in zip(
        text_chunks, embeddings_list)
  ]
  embeddings_list_successful = np.stack(
    [embedding for embedding in embeddings_list if embedding is not None]
  )
  return is_successful, embeddings_list_successful

# Generator function to yield batches of text_chunks
def _generate_batches(text_chunks: List[str],
                      batch_size: int) -> Generator[List[str], None, None]:
  """
  Generate batches of text_chunks
  """
  for i in range(0, len(text_chunks), batch_size):
    yield text_chunks[i: i + batch_size]

def generate_embeddings(batch: List[str], embedding_type: str) -> \
    List[Optional[List[float]]]:

  Logger.info(f"generating embeddings for embedding type {embedding_type}")

  if embedding_type in LANGCHAIN_EMBEDDING_MODELS:
    embeddings = get_langchain_embeddings(embedding_type, batch)
  elif embedding_type in VERTEX_EMBEDDING_MODELS:
    embeddings = get_vertex_embeddings(embedding_type, batch)
  elif embedding_type in LLM_SERVICE_EMBEDDING_MODELS:
    embeddings = get_llm_service_embeddings(embedding_type, batch)
  else:
    raise InternalServerError(f"Unsupported embedding type {embedding_type}")
  return embeddings

def get_vertex_embeddings(embedding_type: str,
    sentence_list: List[str]) -> List[Optional[List[float]]]:
  """
  Generate an embedding from a Vertex model
  Args:
    embedding_type: str - vertex model identifier
    sentence_list: list of text chunks to generate embeddings for
  Returns:
    list of embedding vectors (each vector is a list of floats)
  """
  vertex_model = TextEmbeddingModel.from_pretrained(
      GOOGLE_LLM.get(embedding_type))
  try:
    embeddings = vertex_model.get_embeddings(sentence_list)

    return_value = [embedding.values for embedding in embeddings]

    return return_value
  except Exception:
    return [None for _ in range(len(sentence_list))]

def get_langchain_embeddings(embedding_type: str,
    sentence_list: List[str]) -> List[Optional[List[float]]]:
  """
  Generate an embedding from a langchain model
  Args:
    embedding_type: str - lancghain model identifier
    sentence_list: list of text chunks to generate emneddings for
  Returns:
    list of embedding vectors (each vector is a list of floats)
  """
  langchain_embedding = LANGCHAIN_LLM.get(embedding_type)
  embeddings = langchain_embedding.embed_documents(sentence_list)
  return embeddings

def get_llm_service_embeddings(embedding_type: str,
    sentence_list: List[str]) -> (List)[Optional[List[float]]]:
  """
  Call LLM Service provider to generate embeddings

  Args:
    embedding_type: str - langchain model identifier
    sentence_list: list of text chunks to generate emneddings for
  Returns:
    list of embedding vectors (each vector is a list of floats)
  """
  llm_service_config = LLM_SERVICE_MODELS.get(embedding_type)
  auth_client = UserCredentials(llm_service_config.get("user"),
                                llm_service_config.get("password"))
  auth_token = auth_client.get_id_token()

  # start with base url of the LLM service we are calling
  api_url = llm_service_config.get("api_base_url")
  path = "/llm/embedding"
  api_url = api_url + path

  embeddings_return = []
  for text in sentence_list:
    request_body = {
      "text": text,
      "embedding_type": embedding_type
    }
    Logger.info(f"Sending LLM service request to {api_url}")
    resp = post_method(api_url,
                       request_body=request_body,
                       token=auth_token)
    if resp.status_code != 200:
      raise InternalServerError(
        f"Error status {resp.status_code}: {str(resp)}")

    json_response = resp.json()

    Logger.info(f"Got LLM service response {json_response}")
    embeddings_json = json_response["data"]
    embeddings_array = json.loads(embeddings_json)
    embeddings_return.append(embeddings_array)

  return embeddings_return


class LangchainEmbeddings(Embeddings):
  """ Langchain wrapper for our embeddings """
  def embed_query(self, text: str) -> List[float]:
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL
    embeddings = get_embeddings([text], embedding_type)
    return embeddings[0]

  def embed_documents(self, texts: List[str]) -> List[List[float]]:
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL
    _, embeddings = get_embeddings(texts, embedding_type)
    return embeddings
