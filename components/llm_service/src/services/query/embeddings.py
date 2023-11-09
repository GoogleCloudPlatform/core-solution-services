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
Query Embedddings
"""
import time
import functools
from typing import List, Optional, Generator, Tuple
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from vertexai.preview.language_models import TextEmbeddingModel

from config import GOOGLE_LLM, DEFAULT_QUERY_EMBEDDING_MODEL

def get_embedding_batched(
    text_chunks: List[str], api_calls_per_second: int = 10, batch_size: int = 5
) -> Tuple[List[bool], np.ndarray]:
  """ get embeddings for a list of text strings """

  embeddings_list: List[List[float]] = []

  # Prepare the batches using a generator
  batches = _generate_batches(text_chunks, batch_size)

  seconds_per_job = 1 / api_calls_per_second

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


def encode_texts_to_embeddings(
        sentence_list: List[str]) -> List[Optional[List[float]]]:
  """ encode text using Vertex AI embedding model """
  model = TextEmbeddingModel.from_pretrained(
      GOOGLE_LLM.get(DEFAULT_QUERY_EMBEDDING_MODEL))
  try:
    embeddings = model.get_embeddings(sentence_list)
    return [embedding.values for embedding in embeddings]
  except Exception:
    return [None for _ in range(len(sentence_list))]


# Generator function to yield batches of text_chunks
def _generate_batches(text_chunks: List[str],
                      batch_size: int) -> Generator[List[str], None, None]:
  """ generate batches of text_chunks """
  for i in range(0, len(text_chunks), batch_size):
    yield text_chunks[i: i + batch_size]


