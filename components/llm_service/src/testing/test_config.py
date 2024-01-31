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

""" Config used for testing in unit tests """
# pylint: disable=line-too-long,unused-argument
import os
from langchain.schema import (Generation, ChatGeneration, LLMResult)
from langchain.schema.messages import AIMessage
from config import (COHERE_LLM_TYPE,
                    OPENAI_LLM_TYPE_GPT3_5, OPENAI_LLM_TYPE_GPT4,
                    OPENAI_LLM_TYPE_GPT4_LATEST,
                    VERTEX_LLM_TYPE_BISON_TEXT,
                    VERTEX_LLM_TYPE_BISON_CHAT,
                    VERTEX_LLM_TYPE_GEMINI_PRO,
                    VERTEX_LLM_TYPE_GEMINI_PRO_VISION,
                    PROVIDER_LANGCHAIN, PROVIDER_VERTEX,
                    PROVIDER_TRUSS,
                    PROVIDER_MODEL_GARDEN,
                    VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT,
                    TRUSS_LLM_LLAMA2_CHAT,
                    KEY_PROVIDER, KEY_IS_CHAT, KEY_IS_MULTI, KEY_ENABLED,
                    KEY_MODEL_CLASS, KEY_MODEL_PARAMS, KEY_MODEL_NAME,
                    KEY_MODEL_ENDPOINT)

API_URL = "http://localhost/llm-service/api/v1"

TESTING_FOLDER_PATH = os.path.join(os.getcwd(), "testing")

FAKE_PREDICTION_RESPONSE = "test prediction"

FAKE_GENERATE_RESPONSE = "test generation"

FAKE_LANGCHAIN_GENERATION = Generation(text=FAKE_GENERATE_RESPONSE)

FAKE_CHAT_RESPONSE = ChatGeneration(message=AIMessage(
                                    content=FAKE_GENERATE_RESPONSE))

FAKE_GENERATE_RESULT = LLMResult(generations=[[FAKE_LANGCHAIN_GENERATION]])

FAKE_CHAT_RESULT = LLMResult(generations=[[FAKE_CHAT_RESPONSE]])

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
  },
  OPENAI_LLM_TYPE_GPT4: {
    KEY_PROVIDER: PROVIDER_LANGCHAIN,
    KEY_IS_CHAT: True,
    KEY_ENABLED: True,
    KEY_MODEL_CLASS: FakeModelClass()
  },
  OPENAI_LLM_TYPE_GPT4_LATEST: {
    KEY_PROVIDER: PROVIDER_LANGCHAIN,
    KEY_IS_CHAT: True,
    KEY_ENABLED: True,
    KEY_MODEL_CLASS: FakeModelClass()
  }
}

TEST_VERTEX_CONFIG = {
  KEY_MODEL_PARAMS: {
    "temperature": 0.2,
    "max_tokens": 900,
    "top_p": 1.0,
    "top_k": 10
  },
  VERTEX_LLM_TYPE_BISON_CHAT: {
    KEY_PROVIDER: PROVIDER_VERTEX,
    KEY_IS_CHAT: True,
    KEY_ENABLED: True,
    KEY_MODEL_NAME: "chat-bison@002"
  },
  VERTEX_LLM_TYPE_BISON_TEXT: {
    KEY_PROVIDER: PROVIDER_VERTEX,
    KEY_IS_CHAT: False,
    KEY_ENABLED: True,
    KEY_MODEL_NAME: "text-bison@002"
  },
  VERTEX_LLM_TYPE_GEMINI_PRO: {
    KEY_PROVIDER: PROVIDER_VERTEX,
    KEY_IS_CHAT: True,
    KEY_IS_MULTI: False,
    KEY_ENABLED: True,
    KEY_MODEL_NAME: "gemini-pro"
  },
  VERTEX_LLM_TYPE_GEMINI_PRO_VISION: {
    KEY_PROVIDER: PROVIDER_VERTEX,
    KEY_IS_CHAT: True,
    KEY_IS_MULTI: False,
    KEY_ENABLED: True,
    KEY_MODEL_NAME: "gemini-pro-vision"
  }
}

TEST_MODEL_GARDEN_CONFIG = {
  VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT: {
    KEY_PROVIDER: PROVIDER_MODEL_GARDEN,
    KEY_MODEL_ENDPOINT: "fake-endpoint",
    KEY_IS_CHAT: True,
    KEY_MODEL_PARAMS: {
      "temperature": 0.2,
      "max_tokens": 900,
      "top_p": 1.0,
      "top_k": 10
    },
    KEY_ENABLED: True
  }
}

TEST_TRUSS_CONFIG = {
  TRUSS_LLM_LLAMA2_CHAT: {
    KEY_PROVIDER: PROVIDER_TRUSS,
    KEY_MODEL_ENDPOINT: "fake-endpoint",
    KEY_IS_CHAT: True,
    KEY_MODEL_PARAMS: {
      "temperature": 0.2,
      "max_tokens": 900,
      "top_p": 1.0,
      "top_k": 10
    },
    KEY_ENABLED: True
  }
}

