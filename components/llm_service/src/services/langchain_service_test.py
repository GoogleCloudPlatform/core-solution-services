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
import os
import pytest
from unittest import mock
from services.langchain_service import langchain_llm_generate
from common.models import User, UserChat
from schemas.schema_examples import (CHAT_EXAMPLE, USER_EXAMPLE)
from testing.test_config import (FAKE_GENERATE_RESPONSE,
                                 FAKE_GENERATE_RESULT,
                                 FAKE_CHAT_RESULT,
                                 FAKE_CHAT_RESPONSE)
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from langchain.schema import Generation

os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"

with mock.patch(
    "common.utils.secrets.get_secret",
        side_effect=mock.MagicMock()) as mok:
  with mock.patch("langchain.chat_models.ChatOpenAI"):
    with mock.patch("langchain.llms.Cohere"):
      from config import OPENAI_LLM_TYPE_GPT3_5, COHERE_LLM_TYPE

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"

FAKE_LANGCHAIN_GENERATION = Generation(text=FAKE_GENERATE_RESPONSE)


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
async def test_langchain_llm_generate():
  prompt = "test prompt"
  with mock.patch("langchain.llms.Cohere.agenerate",
                  return_value=FAKE_GENERATE_RESULT):
    response = await langchain_llm_generate(prompt, COHERE_LLM_TYPE)
    assert response == FAKE_GENERATE_RESPONSE, "generated LLM response"


@pytest.mark.asyncio
async def test_langchain_llm_generate_chat(create_user, test_chat):
  prompt = "test prompt"
  with mock.patch("langchain.chat_models.ChatOpenAI.agenerate",
                  return_value=FAKE_CHAT_RESULT):
    response = await langchain_llm_generate(prompt, OPENAI_LLM_TYPE_GPT3_5,
                                            test_chat)
    assert response == FAKE_GENERATE_RESPONSE, "generated LLM chat response"
