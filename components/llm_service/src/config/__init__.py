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
Config for LLM service
"""
from config.config import (
    # platform config
    PROJECT_ID,
    GCP_PROJECT,
    REGION,
    SKAFFOLD_NAMESPACE,
    GKE_CLUSTER,
    GCP_ZONE,
    DATABASE_PREFIX,
    USER_MANAGEMENT_BASE_URL,
    RULES_ENGINE_BASE_URL,
    SERVICES,

    # service config
    PORT,
    API_BASE_URL,
    CONTAINER_NAME,
    DEPLOYMENT_NAME,
    SERVICE_NAME,
    PAYLOAD_FILE_SIZE,
    ERROR_RESPONSES,
    JOB_NAMESPACE,
    auth_client,

    # secrets
    LLM_BACKEND_ROBOT_USERNAME,
    LLM_BACKEND_ROBOT_PASSWORD,

    # LLM types
    LLM_TYPES,
    CHAT_LLM_TYPES,
    OPENAI_LLM_TYPE_GPT3_5,
    OPENAI_LLM_TYPE_GPT4,
    COHERE_LLM_TYPE,
    VERTEX_LLM_TYPE_BISON_TEXT,
    VERTEX_LLM_TYPE_BISON_CHAT,

    # LLM config
    ENABLE_OPENAI_LLM,
    ENABLE_COHERE_LLM,

    # LLM models and collections of models
    DEFAULT_QUERY_CHAT_MODEL,
    DEFAULT_QUERY_EMBEDDING_MODEL,
    GOOGLE_LLM,
    LANGCHAIN_LLM,
    EMBEDDING_MODELS,

    # agent config
    AGENT_CONFIG_PATH,
    )

from config.vector_store_config import (
  DEFAULT_VECTOR_STORE,
  VECTOR_STORES
  )

