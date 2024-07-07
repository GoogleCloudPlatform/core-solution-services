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
import asyncio
import json
from typing import List, Optional, Generator, Tuple
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from vertexai.preview.language_models import TextEmbeddingModel
from vertexai.vision_models import (Image, MultiModalEmbeddingModel)
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import post_method
from common.utils.token_handler import UserCredentials
from config import (get_model_config, get_provider_embedding_types,
                    KEY_MODEL_NAME, KEY_MODEL_CLASS, KEY_MODEL_ENDPOINT,
                    KEY_MODEL_TOKEN_LIMIT,
                    PROVIDER_VERTEX, PROVIDER_LANGCHAIN, PROVIDER_LLM_SERVICE,
                    DEFAULT_QUERY_EMBEDDING_MODEL,
                    DEFAULT_QUERY_MULTI_EMBEDDING_MODEL,
                    REGION)
from langchain.schema.embeddings import Embeddings

# pylint: disable=broad-exception-caught

# per Vertex docs
# https://cloud.google.com/vertex-ai/generative-ai/docs/embeddings/get-text-embeddings#get_text_embeddings_for_a_snippet_of_text
# if region is us-central1 items per request is 250, in other regions it is 5
if REGION == "us-central1":
  # Limit to 50, even though the max is 250. There is an undocumented
  # token limit across all chunks of 20000, and with 250 chunks we often
  # exceeded the 20K limit.
  ITEMS_PER_REQUEST = 50
else:
  ITEMS_PER_REQUEST = 5

Logger = Logger.get_logger(__file__)

async def get_embeddings(
    text_chunks: List[str], embedding_type: str = None) -> (
    Tuple)[List[bool], np.ndarray]:
  """
  Get embeddings for a list of text strings.

  Args:
    text_chunks: list of text chunks to generate embeddings for
    embedding_type: embedding model id
  Returns:
    Tuple of (list of booleans for chunk true if embeddings were generated,
              numpy array of embeddings indexed by chunks)
  """
  if embedding_type is None or embedding_type == "":
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL

  Logger.info(f"generating embeddings with {embedding_type}")

  is_successful, embeddings = await _generate_embeddings_batched(
      embedding_type,
      text_chunks)

  return is_successful, embeddings

async def get_multi_embeddings(
    user_text: List[str], user_file_bytes: str,
    embedding_type: str = None) -> (dict):
  """
  Get multimodal embeddings for a string and image or video file

  Args:
    user_text: text context to generate embeddings for
    embedding_type: embedding model id
    user_file_bytes: the bytes of the file provided by the user
  Returns:
    dictionary of embedding vectors for both text and image
  """
  if embedding_type is None or embedding_type == "":
    embedding_type = DEFAULT_QUERY_MULTI_EMBEDDING_MODEL

  Logger.info(f"generating multimodal embeddings with {embedding_type}")

  embeddings = await generate_multi_embeddings(
      user_text, embedding_type,
      user_file_bytes)

  return embeddings

async def _generate_embeddings_batched(embedding_type,
                                       text_chunks):
  embeddings_list: List[List[float]] = []

  # Prepare the batches using a generator
  batches = _generate_batches(text_chunks, ITEMS_PER_REQUEST)

  loop = asyncio.get_running_loop()
  with ThreadPoolExecutor() as pool:
    futures = []
    for batch in batches:
      futures.append(
        loop.run_in_executor(
            pool, generate_embeddings, batch, embedding_type)
      )
    futures = await asyncio.gather(*futures)
    for future in futures:
      embeddings_list.extend(future)

  is_successful = [
      embedding is not None for sentence, embedding in zip(
        text_chunks, embeddings_list)
  ]
  try:
    embeddings_list_successful = np.stack(
      [embedding for embedding in embeddings_list if embedding is not None]
    )
  except ValueError as e:
    Logger.error(f"error generating embeddings: {str(e)}")
    embeddings_list_successful = []
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
  """
  Generate embeddings for a list of strings
  Args:
    batch: list of text chunks to generate embeddings for
    embedding_type: str - model identifier
  Returns:
    list of embedding vectors (each vector is a list of floats)
  """

  Logger.info(f"generating embeddings for embedding type {embedding_type}")

  if embedding_type in get_provider_embedding_types(PROVIDER_LANGCHAIN):
    embeddings = get_langchain_embeddings(embedding_type, batch)
  elif embedding_type in get_provider_embedding_types(PROVIDER_VERTEX):
    embeddings = get_vertex_embeddings(embedding_type, batch)
  elif embedding_type in get_provider_embedding_types(PROVIDER_LLM_SERVICE):
    embeddings = get_llm_service_embeddings(embedding_type, batch)
  else:
    raise InternalServerError(f"Unsupported embedding type {embedding_type}")
  return embeddings

async def generate_multi_embeddings(user_text: str, embedding_type: str,
          user_file_bytes: bytes) -> (dict):
  """
  Generate embeddings for a list of strings
  Args:
    user_text: str - context text to generate embeddings for
    embedding_type: str - model identifier
    user_file_bytes: bytes - image bytes to generate embeddings for
  Returns:
    dictionary of embedding vectors for both text and image
  """

  Logger.info(f"generating embeddings for embedding type {embedding_type}")

  if embedding_type in get_provider_embedding_types(PROVIDER_VERTEX):
    embeddings = await get_vertex_multi_embeddings(embedding_type, user_text,
                                                   user_file_bytes)
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
  google_llm = get_model_config().get_provider_value(
      PROVIDER_VERTEX, KEY_MODEL_NAME, embedding_type)
  if google_llm is None:
    raise RuntimeError(
        f"Vertex model name not found for embedding type {embedding_type}")

  # check token length for each chunk
  # if the limit is exeeded just log the error - the API will silently truncate
  # the text
  token_limit = get_model_config().get_config_value(
      embedding_type, KEY_MODEL_TOKEN_LIMIT, None)
  if token_limit:
    for chunk in sentence_list:
      if len(chunk) > token_limit:
        Logger.error(
            f"chunk exceeds model {embedding_type} token limit {token_limit}")
  Logger.info(f"generating Vertex embeddings for {len(sentence_list)} chunk(s)"
              f" embedding model {google_llm}")
  vertex_model = TextEmbeddingModel.from_pretrained(google_llm)
  try:
    embeddings = vertex_model.get_embeddings(sentence_list)

    return_value = [embedding.values for embedding in embeddings]

    return return_value
  except Exception as e:
    Logger.error(f"error generating Vertex embeddings {str(e)}")
    return [None for _ in range(len(sentence_list))]

async def get_vertex_multi_embeddings(embedding_type: str,
    user_text: str, user_file_bytes: bytes) -> (dict):
  """
  Generate a image embedding from a Vertex model
  Args:
    embedding_type: str - vertex model identifier
    user_text: str - context text to generate embeddings for
    user_file_bytes: bytes - image bytes to generate embeddings for
  Returns:
    dictionary of embedding vectors for both text and image
  """
  google_llm = get_model_config().get_provider_value(
      PROVIDER_VERTEX, KEY_MODEL_NAME, embedding_type)
  if google_llm is None:
    raise RuntimeError(
        f"Vertex model name not found for embedding type {embedding_type}")

  def _async_vertex_multi_embeddings():
    try:
      user_file_image = Image(image_bytes=user_file_bytes)
      vertex_model = MultiModalEmbeddingModel.from_pretrained(
        google_llm)
      embeddings = vertex_model.get_embeddings(
        image=user_file_image,
        contextual_text=user_text
      )

      return_value = {}
      return_value["text_embeddings"] = embeddings.text_embedding
      return_value["image_embeddings"] = embeddings.image_embedding

      return return_value
    except Exception as e:
      Logger.error(f"error generating Vertex embeddings {str(e)}")
      raise e

  return_value = await asyncio.to_thread(_async_vertex_multi_embeddings)

  return return_value

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
  langchain_embedding = get_model_config().get_provider_value(
      PROVIDER_LANGCHAIN, KEY_MODEL_CLASS, embedding_type)
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
  llm_service_config = get_model_config().get_provider_config(
      PROVIDER_LLM_SERVICE, embedding_type)
  auth_client = UserCredentials(llm_service_config.get("user"),
                                llm_service_config.get("password"))
  auth_token = auth_client.get_id_token()

  # start with base url of the LLM service we are calling
  api_url = llm_service_config.get(KEY_MODEL_ENDPOINT)
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
    _, embeddings = asyncio.get_event_loop().run_until_complete(
        get_embeddings([text], embedding_type))
    return embeddings[0]

  def embed_documents(self, texts: List[str]) -> List[List[float]]:
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL
    _, embeddings = asyncio.get_event_loop().run_until_complete(
        get_embeddings(texts, embedding_type))
    return embeddings

  async def aembed_documents(self, texts: List[str]) -> List[List[float]]:
    """Asynchronous Embed search docs."""
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL
    _, embeddings = await get_embeddings(texts, embedding_type)
    return embeddings

  async def aembed_query(self, text: str) -> List[float]:
    """Asynchronous Embed query text."""
    embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL
    _, embeddings = await get_embeddings([text], embedding_type)
    return embeddings
