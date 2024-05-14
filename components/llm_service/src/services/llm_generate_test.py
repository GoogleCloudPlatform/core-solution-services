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
  Unit tests for Langchain Service endpoints
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,wrong-import-position
# pylint: disable=unused-variable,ungrouped-imports,import-outside-toplevel
import os
import pytest
from unittest import mock

os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"
os.environ["MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID"] = "fake-endpoint"
os.environ["TRUSS_LLAMA2_ENDPOINT"] = "fake-endpoint"
os.environ["VLLM_GEMMA_ENDPOINT"] = "fake-endpoint"

from services.llm_generate import llm_generate, llm_chat, llm_generate_multi
from fastapi import UploadFile
from google.cloud.aiplatform.models import Prediction
from vertexai.preview.language_models import TextGenerationResponse
from common.models import User, UserChat
from common.testing.firestore_emulator import (firestore_emulator,
                                               clean_firestore)
from common.utils.logging_handler import Logger
from schemas.schema_examples import (CHAT_EXAMPLE, USER_EXAMPLE)

Logger = Logger.get_logger(__file__)

with (mock.patch("common.utils.secrets.get_secret", new=mock.AsyncMock())):
  with mock.patch("langchain.chat_models.ChatOpenAI", new=mock.AsyncMock()):
    with mock.patch("langchain.chat_models.ChatCohere"):
      from testing.test_config import (FAKE_GENERATE_RESPONSE,
                                       FAKE_PREDICTION_RESPONSE,
                                       TEST_COHERE_CONFIG,
                                       TEST_OPENAI_CONFIG,
                                       TEST_VERTEX_CONFIG,
                                       TEST_MODEL_GARDEN_CONFIG,
                                       TEST_TRUSS_CONFIG,
                                       TEST_VLLM_CONFIG)
      from config import (get_model_config,
                          COHERE_LLM_TYPE,
                          OPENAI_LLM_TYPE_GPT3_5,
                          VERTEX_LLM_TYPE_BISON_TEXT,
                          VERTEX_LLM_TYPE_BISON_CHAT,
                          VERTEX_LLM_TYPE_GEMINI_PRO,
                          VERTEX_LLM_TYPE_GEMINI_PRO_VISION,
                          PROVIDER_LANGCHAIN, PROVIDER_VERTEX,
                          PROVIDER_TRUSS, PROVIDER_VLLM,
                          PROVIDER_MODEL_GARDEN,
                          VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT,
                          TRUSS_LLM_LLAMA2_CHAT, VLLM_LLM_GEMMA_CHAT)

FAKE_GOOGLE_RESPONSE = TextGenerationResponse(text=FAKE_GENERATE_RESPONSE,
                                              _prediction_response={})
FAKE_MODEL_GARDEN_RESPONSE = Prediction(predictions=[FAKE_PREDICTION_RESPONSE],
                                        deployed_model_id="123")
FAKE_TRUSS_RESPONSE = {
  "data": {"generated_text": FAKE_GENERATE_RESPONSE}
}
FAKE_VLLM_RESPONSE = {
    "data": {"generated_text": FAKE_GENERATE_RESPONSE}
}

FAKE_FILE_NAME = "test.png"
FAKE_FILE_TYPE = "image/png"
FAKE_PROMPT = "test prompt"


@pytest.fixture
def create_user(firestore_emulator, clean_firestore):
  user_dict = USER_EXAMPLE
  user = User.from_dict(user_dict)
  user.save()


@pytest.fixture
def test_chat(firestore_emulator, clean_firestore):
  chat_dict = CHAT_EXAMPLE
  chat = UserChat.from_dict(chat_dict)
  chat.save()
  return chat


@pytest.mark.asyncio
async def test_llm_generate(clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_COHERE_CONFIG
  }
  get_model_config().llm_models = TEST_COHERE_CONFIG

  response = await llm_generate(FAKE_PROMPT, COHERE_LLM_TYPE)

  assert response == FAKE_GENERATE_RESPONSE


@pytest.mark.asyncio
async def test_llm_chat(clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_OPENAI_CONFIG
  }
  get_model_config().llm_models = TEST_OPENAI_CONFIG
  response = await llm_chat(FAKE_PROMPT, OPENAI_LLM_TYPE_GPT3_5)

  assert response == FAKE_GENERATE_RESPONSE


@pytest.mark.asyncio
async def test_llm_chat_resume(clean_firestore, test_chat):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_OPENAI_CONFIG
  }
  get_model_config().llm_models = TEST_OPENAI_CONFIG
  response = await llm_chat(
      FAKE_PROMPT, OPENAI_LLM_TYPE_GPT3_5, test_chat)

  assert response == FAKE_GENERATE_RESPONSE


@pytest.mark.asyncio
async def test_llm_generate_google(clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_VERTEX: TEST_VERTEX_CONFIG
  }
  get_model_config().llm_models = TEST_VERTEX_CONFIG
  with mock.patch(
      "vertexai.preview.language_models.TextGenerationModel.predict_async",
          return_value=FAKE_GOOGLE_RESPONSE):
    response = await llm_generate(
      FAKE_PROMPT, VERTEX_LLM_TYPE_BISON_TEXT)

  assert response == FAKE_GENERATE_RESPONSE


@pytest.mark.asyncio
async def test_llm_generate_multi(clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_VERTEX: TEST_VERTEX_CONFIG
  }
  get_model_config().llm_models = TEST_VERTEX_CONFIG

  with open(FAKE_FILE_NAME, "ab") as f:
    pass
  fake_file=open(FAKE_FILE_NAME, "rb")
  os.remove(FAKE_FILE_NAME)
  fake_upload_file = UploadFile(file=fake_file, filename=FAKE_FILE_NAME)
  fake_file_bytes = await fake_upload_file.read()

  with mock.patch(
  "vertexai.preview.generative_models.GenerativeModel.generate_content_async",
  return_value=FAKE_GOOGLE_RESPONSE):
    response = await llm_generate_multi(FAKE_PROMPT, fake_file_bytes,
                            FAKE_FILE_TYPE, VERTEX_LLM_TYPE_GEMINI_PRO_VISION)

  fake_file.close()
  assert response == FAKE_GENERATE_RESPONSE


@pytest.mark.asyncio
async def test_llm_chat_google(clean_firestore, test_chat):
  get_model_config().llm_model_providers = {
    PROVIDER_VERTEX: TEST_VERTEX_CONFIG
  }
  get_model_config().llm_models = TEST_VERTEX_CONFIG
  with mock.patch(
          "vertexai.preview.language_models.ChatSession.send_message_async",
          return_value=FAKE_GOOGLE_RESPONSE):
    response = await llm_chat(
      FAKE_PROMPT, VERTEX_LLM_TYPE_BISON_CHAT)

  assert response == FAKE_GENERATE_RESPONSE


@pytest.mark.asyncio
async def test_llm_chat_google_resume(clean_firestore, test_chat):
  get_model_config().llm_model_providers = {
    PROVIDER_VERTEX: TEST_VERTEX_CONFIG
  }
  get_model_config().llm_models = TEST_VERTEX_CONFIG
  with mock.patch(
          "vertexai.preview.language_models.ChatSession.send_message_async",
          return_value=FAKE_GOOGLE_RESPONSE):
    response = await llm_chat(
      FAKE_PROMPT, VERTEX_LLM_TYPE_BISON_CHAT, test_chat)

  assert response == FAKE_GENERATE_RESPONSE


@pytest.mark.asyncio
async def test_model_garden_predict(clean_firestore, test_chat):
  get_model_config().llm_model_providers = {
    PROVIDER_MODEL_GARDEN: TEST_MODEL_GARDEN_CONFIG
  }
  get_model_config().llm_models = TEST_MODEL_GARDEN_CONFIG

  with mock.patch(
          "google.cloud.aiplatform.Endpoint.predict_async",
          return_value=FAKE_MODEL_GARDEN_RESPONSE):
    response = await llm_chat(
      FAKE_PROMPT, VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT)

  assert response == FAKE_PREDICTION_RESPONSE


@pytest.mark.asyncio
async def test_llm_truss_service_predict(clean_firestore, test_chat):
  get_model_config().llm_model_providers = {
    PROVIDER_TRUSS: TEST_TRUSS_CONFIG
  }
  get_model_config().llm_models = TEST_TRUSS_CONFIG
  with mock.patch(
          "services.llm_generate.post_method",
          return_value=mock.Mock(status_code=200,
                                 json=lambda: FAKE_TRUSS_RESPONSE)):
    response = await llm_chat(
      FAKE_PROMPT, TRUSS_LLM_LLAMA2_CHAT)

  assert response == FAKE_GENERATE_RESPONSE

@pytest.mark.asyncio
async def test_llm_vllm_service_predict(clean_firestore, test_chat):
  get_model_config().llm_model_providers = {
    PROVIDER_VLLM: TEST_VLLM_CONFIG
  }
  get_model_config().llm_models = TEST_VLLM_CONFIG
  with mock.patch(
          "services.llm_generate.post_method",
          return_value=mock.Mock(status_code=200,
                                 json=lambda: FAKE_VLLM_RESPONSE)):
    response = await llm_chat(
      FAKE_PROMPT, VLLM_LLM_GEMMA_CHAT)

  assert response == FAKE_GENERATE_RESPONSE
