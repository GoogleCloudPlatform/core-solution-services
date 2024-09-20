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
  Unit tests for LLM Service embeddings
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,ungrouped-imports,unused-import
import numpy.testing as npt
import numpy as np
import pytest
from unittest import mock
from common.utils.logging_handler import Logger
from common.utils.config import set_env_var
from vertexai.preview.language_models import TextEmbedding
from vertexai.preview.vision_models import MultiModalEmbeddingResponse
from services.embeddings import get_embeddings, get_multimodal_embeddings
with set_env_var("PG_HOST", ""):
  from config import (get_model_config, DEFAULT_QUERY_EMBEDDING_MODEL,
                      DEFAULT_QUERY_MULTI_EMBEDDING_MODEL)

Logger = Logger.get_logger(__file__)

FAKE_VERTEX_TEXT_EMBEDDINGS = \
    [TextEmbedding([0.0]), TextEmbedding([0.1]), TextEmbedding([0.2])]
FAKE_TEXT_EMBEDDINGS = \
    np.array([embedding.values for embedding in FAKE_VERTEX_TEXT_EMBEDDINGS])

FAKE_VERTEX_MULTI_EMBEDDINGS = \
    MultiModalEmbeddingResponse(_prediction_response=None,
                                text_embedding=[0.0], image_embedding=[0.1])

FAKE_MULTI_EMBEDDINGS = {
  "text": [0.0],
  "image": [0.1]
  # TODO: Also set value of "video" key
  # and potentially "audio" key
}

FAKE_MULTI_IMAGE_BYTES = \
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAAXNSR0IArs\
   4c6QAAAA1JREFUGFdjYGBg+A8AAQQBAHAgZQsAAAAASUVORK5CYII="

@pytest.mark.asyncio
@mock.patch("services.embeddings.TextEmbeddingModel.get_embeddings")
async def test_get_embeddings(mock_get_vertex_embeddings):
  mock_get_vertex_embeddings.return_value = FAKE_VERTEX_TEXT_EMBEDDINGS
  embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL
  text_chunks = ["test sentence 1"]
  is_successful, embeddings = await get_embeddings(text_chunks, embedding_type)
  assert all(is_successful)
  npt.assert_array_equal(embeddings, FAKE_TEXT_EMBEDDINGS)

@pytest.mark.asyncio
@mock.patch("services.embeddings.TextEmbeddingModel.get_embeddings")
async def test_get_embeddings_empty(mock_get_vertex_embeddings):
  mock_get_vertex_embeddings.return_value = []
  embedding_type = DEFAULT_QUERY_EMBEDDING_MODEL
  text_chunks = []
  is_successful, embeddings = await get_embeddings(text_chunks, embedding_type)
  assert not is_successful
  npt.assert_array_equal(embeddings, [])

@pytest.mark.asyncio
@mock.patch(
    "services.embeddings.MultiModalEmbeddingModel.get_embeddings")
async def test_get_embeddings_multi(mock_get_vertex_embeddings):
  mock_get_vertex_embeddings.return_value = FAKE_VERTEX_MULTI_EMBEDDINGS
  embedding_type = DEFAULT_QUERY_MULTI_EMBEDDING_MODEL
  text_chunks = []
  embeddings = await get_multimodal_embeddings(
      text_chunks, FAKE_MULTI_IMAGE_BYTES, embedding_type)
  assert embeddings == FAKE_MULTI_EMBEDDINGS
