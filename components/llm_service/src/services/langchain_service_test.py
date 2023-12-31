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
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports
# pylint: disable=wrong-import-position
import os
import pytest

os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

from unittest import mock
from services.langchain_service import langchain_llm_generate
from common.models import User, UserChat
from schemas.schema_examples import (CHAT_EXAMPLE, USER_EXAMPLE)
from testing.test_config import (FAKE_GENERATE_RESPONSE,
                                 FAKE_GENERATE_RESULT,
                                 FAKE_CHAT_RESULT)
from common.testing.firestore_emulator import firestore_emulator, clean_firestore

with mock.patch(
    "common.utils.secrets.get_secret",
        side_effect=mock.MagicMock()) as mok:
  with mock.patch("langchain.chat_models.ChatOpenAI"):
    with mock.patch("langchain.chat_models.ChatCohere"):
      from config import (get_model_config,
                          KEY_IS_CHAT, KEY_ENABLED, KEY_PROVIDER, KEY_MODEL_CLASS,
                          PROVIDER_LANGCHAIN, COHERE_LLM_TYPE,
                          OPENAI_LLM_TYPE_GPT3_5)

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

class FakeModelClass:
  async def agenerate(self, prompts):
    return FAKE_CHAT_RESULT

TEST_COHERE_CONFIG = {
  COHERE_LLM_TYPE: {
    KEY_PROVIDER: PROVIDER_LANGCHAIN,
    KEY_IS_CHAT: True,
    KEY_ENABLED: True,
    KEY_MODEL_CLASS: FakeModelClass()
  }
}

TEST_OPENAI_CONFIG = {
  OPENAI_LLM_TYPE_GPT3_5: {
    KEY_PROVIDER: PROVIDER_LANGCHAIN,
    KEY_IS_CHAT: True,
    KEY_ENABLED: True,
    KEY_MODEL_CLASS: FakeModelClass()
  }
}


@pytest.fixture
def create_user(firestore_emulator, clean_firestore, scope="module"):
  user_dict = USER_EXAMPLE
  user = User.from_dict(user_dict)
  user.save()


@pytest.fixture
def test_chat(firestore_emulator, clean_firestore, scope="module"):
  chat_dict = CHAT_EXAMPLE
  chat = UserChat.from_dict(chat_dict)
  chat.save()
  return chat


@pytest.mark.asyncio
async def test_langchain_llm_generate(clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_COHERE_CONFIG
  }
  get_model_config().llm_models = TEST_COHERE_CONFIG

  prompt = "test prompt"
  response = await langchain_llm_generate(prompt, COHERE_LLM_TYPE)
  assert response == FAKE_GENERATE_RESPONSE, "generated LLM response"


@pytest.mark.asyncio
async def test_langchain_llm_generate_chat(test_chat, clean_firestore):
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_OPENAI_CONFIG
  }
  get_model_config().llm_models = TEST_OPENAI_CONFIG
  prompt = "test prompt"
  response = await langchain_llm_generate(prompt, OPENAI_LLM_TYPE_GPT3_5,
                                          test_chat)
  assert response == FAKE_GENERATE_RESPONSE, "generated LLM chat response"
