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
    LLM_SERVICE_PATH,
    PORT,
    API_BASE_URL,
    CONTAINER_NAME,
    DEPLOYMENT_NAME,
    SERVICE_NAME,
    PAYLOAD_FILE_SIZE,
    ERROR_RESPONSES,
    JOB_NAMESPACE,
    auth_client,

    # model config object
    get_model_config,
    MODEL_CONFIG_PATH,

    # agent config
    AGENT_CONFIG_PATH,
    AGENT_DATASET_CONFIG_PATH,
    get_agent_config,
    get_dataset_config,

    # secrets
    LLM_BACKEND_ROBOT_USERNAME,
    LLM_BACKEND_ROBOT_PASSWORD,

    # LLM vendor flags
    ENABLE_OPENAI_LLM,
    ENABLE_COHERE_LLM,

    # default LLM models
    DEFAULT_QUERY_CHAT_MODEL,
    DEFAULT_QUERY_EMBEDDING_MODEL,
    DEFAULT_LLM_TYPE,

    # query engine and other defaults
    DEFAULT_WEB_DEPTH_LIMIT,
    )

from config.model_config import (
    # llm type constants
    OPENAI_LLM_TYPE_GPT3_5,
    OPENAI_LLM_TYPE_GPT4,
    OPENAI_LLM_TYPE_GPT4_LATEST,
    COHERE_LLM_TYPE,
    VERTEX_LLM_TYPE_BISON_TEXT,
    VERTEX_LLM_TYPE_BISON_CHAT,
    VERTEX_LLM_TYPE_BISON_CHAT_LANGCHAIN,
    VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT,
    TRUSS_LLM_LLAMA2_CHAT,

    # model config keys
    KEY_ENABLED,
    KEY_MODELS,
    KEY_PROVIDERS,
    KEY_VENDORS,
    KEY_PROVIDER,
    KEY_EMBEDDINGS,
    KEY_API_KEY,
    KEY_ENV_FLAG,
    KEY_MODEL_CLASS,
    KEY_MODEL_NAME,
    KEY_MODEL_PARAMS,
    KEY_IS_CHAT,
    KEY_MODEL_FILE_URL,
    KEY_MODEL_PATH,
    KEY_MODEL_ENDPOINT,
    KEY_VENDOR,

    # model providers
    PROVIDER_VERTEX,
    PROVIDER_MODEL_GARDEN,
    PROVIDER_LANGCHAIN,
    PROVIDER_TRUSS,
    PROVIDER_LLM_SERVICE,

    # model vendors
    VENDOR_OPENAI,
    VENDOR_COHERE,
    )

from config.vector_store_config import (
  DEFAULT_VECTOR_STORE,
  VECTOR_STORES,
  PG_HOST
)

from config.utils import (
  get_provider_models,
  get_provider_value,
  get_provider_embedding_types,
  get_provider_config,
  get_provider_model_config
)
