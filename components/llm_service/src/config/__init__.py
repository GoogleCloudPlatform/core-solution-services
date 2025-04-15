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
    get_agent_config,
    get_dataset_config,

    # document manifest config
    DEFAULT_DOCUMENT_MANIFEST_PATH,
    get_default_manifest,

    # secrets
    LLM_BACKEND_ROBOT_USERNAME,
    LLM_BACKEND_ROBOT_PASSWORD,

    # LLM vendor flags
    ENABLE_OPENAI_LLM,
    ENABLE_COHERE_LLM,

    # default LLM models
    DEFAULT_LLM_TYPE,
    DEFAULT_CHAT_LLM_TYPE,
    DEFAULT_QUERY_CHAT_MODEL,
    DEFAULT_QUERY_EMBEDDING_MODEL,
    DEFAULT_QUERY_MULTIMODAL_EMBEDDING_MODEL,
    DEFAULT_MULTIMODAL_LLM_TYPE,
    DEFAULT_CHAT_SUMMARY_MODEL,

    # query engine and other defaults
    DEFAULT_WEB_DEPTH_LIMIT,
    MODALITY_SET,
    )

from config.model_config import (
    ModelConfig,

    # llm type constants
    OPENAI_LLM_TYPE_GPT3_5,
    OPENAI_LLM_TYPE_GPT4,
    OPENAI_LLM_TYPE_GPT4_LATEST,
    COHERE_LLM_TYPE,
    VERTEX_LLM_TYPE_CHAT,
    VERTEX_LLM_TYPE_BISON_TEXT,
    VERTEX_LLM_TYPE_GEMINI_PRO_LANGCHAIN,
    VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT,
    VERTEX_LLM_TYPE_GEMINI_PRO,
    VERTEX_LLM_TYPE_GEMINI_PRO_VISION,
    VERTEX_LLM_TYPE_GEMINI_1_5_PRO,
    VERTEX_LLM_TYPE_GEMINI_FLASH,
    TRUSS_LLM_LLAMA2_CHAT,
    VLLM_LLM_GEMMA_CHAT,

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
    KEY_MODEL_CONTEXT_LENGTH,
    KEY_MODEL_TOKEN_LIMIT,
    KEY_IS_CHAT,
    KEY_IS_MULTI,
    KEY_MODEL_FILE_URL,
    KEY_MODEL_PATH,
    KEY_MODEL_ENDPOINT,
    KEY_VENDOR,
    KEY_ROLE_ACCESS,
    KEY_SUB_PROVIDER,
    KEY_NAME,
    KEY_DEFAULT_SYSTEM_PROMPT,

    # model types
    MODEL_TYPES,

    # model providers
    PROVIDER_VERTEX,
    PROVIDER_MODEL_GARDEN,
    PROVIDER_LANGCHAIN,
    PROVIDER_TRUSS,
    PROVIDER_VLLM,
    PROVIDER_LLM_SERVICE,

    # model vendors
    VENDOR_OPENAI,
    VENDOR_COHERE,

    # model sub-providers
    SUB_PROVIDER_OPENAPI,
    )

from config.vector_store_config import (
  DEFAULT_VECTOR_STORE,
  VECTOR_STORES,
  PG_HOST
)

from config.onedrive_config import (
  ONEDRIVE_CLIENT_ID,
  ONEDRIVE_TENANT_ID,
  ONEDRIVE_CLIENT_SECRET,
  ONEDRIVE_PRINCIPLE_NAME
)

from config.utils import (
  get_provider_models,
  get_provider_value,
  get_provider_embedding_types,
  get_provider_config,
  get_provider_model_config,
  get_model_config_value,
  get_model_system_prompt
)
