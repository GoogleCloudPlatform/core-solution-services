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
Generate Query embedddings. Currently using Vertex TextEmbedding model.
"""
import time
import functools
from typing import List, Optional, Generator, Tuple
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from vertexai.preview.language_models import TextEmbeddingModel
from config import GOOGLE_LLM, DEFAULT_QUERY_EMBEDDING_MODEL
from langchain.schema.embeddings import Embeddings

# pylint: disable=broad-exception-caught

# Create a rate limit of 300 requests per minute.
API_CALLS_PER_SECOND = int(300 / 60)

# According to the docs, each request can process 5 instances per request
ITEMS_PER_REQUEST = 5


def get_embeddings(text_chunks: List[str]) -> Tuple[List[bool], np.ndarray]:
  """
  Get embeddings for a list of text strings.

  Args:
    text_chunks: list of text chunks to generate embeddings for
  Returns:
    Tuple of (list of booleans for chunk true if embeddings were generated,
              numpy array of embeddings indexed by chunks)
  """

  embeddings_list: List[List[float]] = []

  # Prepare the batches using a generator
  batches = _generate_batches(text_chunks, ITEMS_PER_REQUEST)

  seconds_per_job = 1 / API_CALLS_PER_SECOND

  with ThreadPoolExecutor() as executor:
    futures = []
    for batch in batches:
      futures.append(
          executor.submit(functools.partial(encode_texts_to_embeddings), batch)
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

def encode_texts_to_embeddings(
        sentence_list: List[str]) -> List[Optional[List[float]]]:
  """
  Encode list of strings using Vertex AI embedding model
  """
  model = TextEmbeddingModel.from_pretrained(
      GOOGLE_LLM.get(DEFAULT_QUERY_EMBEDDING_MODEL))
  try:
    embeddings = model.get_embeddings(sentence_list)
    return [embedding.values for embedding in embeddings]
  except Exception:
    return [None for _ in range(len(sentence_list))]


class LangchainEmbeddings(Embeddings):
  """ Langchain wrapper for our embeddings """
  def embed_query(self, text: str) -> List[float]:
    embeddings = encode_texts_to_embeddings([text])
    return embeddings[0]

  def embed_documents(self, texts: list(str)) -> List[List[float]]:
    _, embeddings = get_embeddings(texts)
    return embeddings
