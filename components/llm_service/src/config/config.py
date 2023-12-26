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
  LLM Service config file
"""
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught
import json
import os
from common.utils.config import get_environ_flag
from common.utils.gcs_adapter import download_file_from_gcs
from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
from common.utils.token_handler import UserCredentials
from common.utils.http_exceptions import InternalServerError
from schemas.error_schema import (UnauthorizedResponseModel,
                                  InternalServerErrorResponseModel,
                                  ValidationErrorResponseModel)
from google.cloud import secretmanager
from config.model_config import (ModelConfig, PROVIDER_OPENAI, 
                                PROVIDER_VERTEX, PROVIDER_COHERE,
                                PROVIDER_LANGCHAIN, PROVIDER_MODEL_GARDEN,
                                PROVIDER_TRUSS,
                                )

Logger = Logger.get_logger(__file__)
secrets = secretmanager.SecretManagerServiceClient()

PORT = os.environ["PORT"] if os.environ.get("PORT") is not None else 80
PROJECT_ID = os.environ.get("PROJECT_ID")
assert PROJECT_ID, "PROJECT_ID must be set"

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
GCP_PROJECT = PROJECT_ID
DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")
REGION = os.getenv("REGION", "us-central1")

try:
  with open("/var/run/secrets/kubernetes.io/serviceaccount/namespace", "r",
            encoding="utf-8", errors="ignore") as ns_file:
    namespace = ns_file.readline()
    JOB_NAMESPACE = namespace
except FileNotFoundError as e:
  JOB_NAMESPACE = "default"
  Logger.info("Namespace File not found, setting job namespace as default")

LLM_SERVICE_PATH = "llm-service/api/v1"
CONTAINER_NAME = os.getenv("CONTAINER_NAME")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_BASE_URL = os.getenv("API_BASE_URL")
SERVICE_NAME = os.getenv("SERVICE_NAME")
SKAFFOLD_NAMESPACE = os.getenv("SKAFFOLD_NAMESPACE")
GKE_CLUSTER = os.getenv("GKE_CLUSTER")
GCP_ZONE = os.getenv("GCP_ZONE")

PAYLOAD_FILE_SIZE = 1024

ERROR_RESPONSES = {
    500: {
        "model": InternalServerErrorResponseModel
    },
    401: {
        "model": UnauthorizedResponseModel
    },
    422: {
        "model": ValidationErrorResponseModel
    }
}

# load model config object
MODEL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "models.json")
model_config = ModelConfig(MODEL_CONFIG_PATH)
model_config.load_model_config()

# provider enabled flags
ENABLE_GOOGLE_LLM = model_config.is_provider_enabled(PROVIDER_VERTEX)
ENABLE_GOOGLE_MODEL_GARDEN = \
    model_config.is_provider_enabled(PROVIDER_MODEL_GARDEN)
ENABLE_OPENAI_LLM = model_config.is_provider_enabled(PROVIDER_OPENAI)
ENABLE_COHERE_LLM = model_config.is_provider_enabled(PROVIDER_COHERE)

ENABLE_LLAMA2CPP_LLM = get_environ_flag("ENABLE_LLAMA2CPP_LLM", False)

# truss hosted models
# TODO: delete
ENABLE_TRUSS_LLAMA2 = model_config.is_provider_enabled(PROVIDER_TRUSS)
LLM_TRUSS_MODEL_ENDPOINT = os.getenv("TRUSS_LLAMA2_ENDPOINT", "http://truss-llama2-7b-service:8080")

# API Keys
OPENAI_API_KEY = model_config.get_api_key(PROVIDER_OPENAI)
COHERE_API_KEY = model_config.get_api_key(PROVIDER_COHERE)

# LLM types
LLM_TYPES = model_config.get_llm_types()
CHAT_LLM_TYPES = model_config.get_chat_llm_types()
OPENAI_LLM_TYPES = model_config.get_provider_llm_types(PROVIDER_OPENAI)
COHERE_LLM_TYPES = model_config.get_provider_llm_types(PROVIDER_COHERE)
GOOGLE_LLM_TYPES = mode_config.get_provider_llm_types(PROVIDER_VERTEX)

# LLM provider config dicts
LANGCHAIN_LLM = model_config.get_provider_config(PROVIDER_LANGCHAIN)
GOOGLE_LLM = model_config.get_provider_config(PROVIDER_VERTEX)
GOOGLE_MODEL_GARDEN = model_config.get_provider_config(PROVIDER_MODEL_GARDEN)
LLM_TRUSS_MODELS = model_config.get_provider_config(PROVIDER_TRUSS)

LLAMA2CPP_MODEL_PATH = None
if ENABLE_LLAMA2CPP_LLM:
  LLAMA2CPP_MODEL_FILE = os.getenv("LLAMA2CPP_MODEL_FILE")
  models_dir = os.path.join(os.path.dirname(__file__), "models/")
  Logger.info(f"llama2cpp model file = {LLAMA2CPP_MODEL_FILE}")

  # download Llama2cpp model file from GCS
  try:
    if LLAMA2CPP_MODEL_FILE.startswith("gs://"):
      LLAMA2CPP_MODEL_PATH = \
          download_file_from_gcs(LLAMA2CPP_MODEL_FILE,
                                 destination_folder_path=models_dir)
    else:
      # assume its a file path
      LLAMA2CPP_MODEL_PATH = LLAMA2CPP_MODEL_FILE

  except Exception as e:
    raise InternalServerError(
        f"Failed to download llama2cpp model file {str(e)}") from e

  Logger.info(f"llama2cpp model path = {LLAMA2CPP_MODEL_PATH}")

  LANGCHAIN_LLM.update({
    LLAMA2CPP_LLM_TYPE: LlamaCpp(model_path=LLAMA2CPP_MODEL_PATH)
  })
  LLM_TYPES.append(LLAMA2CPP_LLM_TYPE)


# TODO: fix model garden config

#if ENABLE_GOOGLE_MODEL_GARDEN:
#  MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID = \
#    os.getenv("MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID")
#  if MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID:
#    GOOGLE_MODEL_GARDEN_TYPES = [VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT]
#    GOOGLE_MODEL_GARDEN = {
#        VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT: MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID,
#    }
#    LLM_TYPES.extend(GOOGLE_MODEL_GARDEN_TYPES)


# read llm service models from json config file
LLM_SERVICE_MODEL_CONFIG_PATH = os.path.join(os.path.dirname(__file__),
                                             "llm_service_models.json")
LLM_SERVICE_MODELS = {}
LLM_SERVICE_EMBEDDING_TYPES = []
try:
  with open(LLM_SERVICE_MODEL_CONFIG_PATH, "r", encoding="utf-8") as file:
    LLM_SERVICE_MODELS = json.load(file)

  # populate credentials in config dict
  for llm_type, llm_config in LLM_SERVICE_MODELS.items():
    auth_password = get_secret(f"llm_service_password_{llm_type}")
    LLM_SERVICE_MODELS[llm_type]["password"] = auth_password

  LLM_SERVICE_MODEL_TYPES = list(LLM_SERVICE_MODELS.keys())
  LLM_TYPES.extend(LLM_SERVICE_MODEL_TYPES)
  LLM_SERVICE_EMBEDDING_TYPES = LLM_SERVICE_MODEL_TYPES
  Logger.info(
      f"Loaded LLM Service-provider models: {LLM_SERVICE_MODEL_TYPES}")
  Logger.info(
      f"Loaded LLM Service-provider embedding models: {LLM_SERVICE_EMBEDDING_TYPES}")
except Exception as e:
  Logger.info(f"Can't load llm_service_models.json: {str(e)}")

Logger.info(f"LLM types loaded {LLM_TYPES}")

DEFAULT_QUERY_CHAT_MODEL = VERTEX_LLM_TYPE_BISON_CHAT

# embedding models
VERTEX_EMBEDDING_TYPES = \
    model_config.get_provider_embedding_types(PROVIDER_VERTEX)
LANGCHAIN_EMBEDDING_TYPES = \
    model_config.get_provider_embedding_types(PROVIDER_LANGCHAIN)
EMBEDDING_TYPES = model_config.get_embedding_types()

DEFAULT_QUERY_EMBEDDING_MODEL = VERTEX_LLM_TYPE_GECKO_EMBEDDING
Logger.info(f"Embedding types loaded {EMBEDDING_TYPES}")

# services config
SERVICES = {
  "user-management": {
    "host": "http://user-management",
    "port": 80,
    "api_path": "/user-management/api/v1",
    "api_url_prefix": "http://user-management:80/user-management/api/v1",
  },
  "tools-service": {
    "host": "http://tools-service",
    "port": 80,
    "api_path": "/tools-service/api/v1",
    "api_url_prefix": "http://tools-service:80/tools-service/api/v1",
  },
  "rules-engine": {
    "host": "http://rules-engine",
    "port": 80,
    "api_path": "/rules-engine/api/v1",
    "api_url_prefix": "http://rules-engine:80/rules-engine/api/v1",
  }
}

USER_MANAGEMENT_BASE_URL = f"{SERVICES['user-management']['host']}:" \
                  f"{SERVICES['user-management']['port']}" \
                  f"/user-management/api/v1"

TOOLS_SERVICE_BASE_URL = f"{SERVICES['tools-service']['host']}:" \
                  f"{SERVICES['tools-service']['port']}" \
                  f"/tools-service/api/v1"

RULES_ENGINE_BASE_URL = f"{SERVICES['rules-engine']['host']}:" \
                  f"{SERVICES['rules-engine']['port']}" \
                  f"/rules-engine/api/v1"

try:
  LLM_BACKEND_ROBOT_USERNAME = get_secret("llm-backend-robot-username")
except Exception as e:
  LLM_BACKEND_ROBOT_USERNAME = None

try:
  LLM_BACKEND_ROBOT_PASSWORD = get_secret("llm-backend-robot-password")
except Exception as e:
  LLM_BACKEND_ROBOT_PASSWORD = None

# Update this config for local development or notebook usage, by adding
# a parameter to the UserCredentials class initializer, to
# pass URL to auth client.
# auth_client = UserCredentials(LLM_BACKEND_ROBOT_USERNAME,
#                               LLM_BACKEND_ROBOT_PASSWORD,
#                               "http://localhost:9004")
# pass URL to auth client for external routes to auth.  Replace dev.domain with
# the externally mapped domain for your dev server
# auth_client = UserCredentials(LLM_BACKEND_ROBOT_USERNAME,
#                               LLM_BACKEND_ROBOT_PASSWORD,
#                               "https://[dev.domain]")

auth_client = UserCredentials(LLM_BACKEND_ROBOT_USERNAME,
                              LLM_BACKEND_ROBOT_PASSWORD)

# agent config
AGENT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "agent_config.json")

AGENT_DATASET_CONFIG_PATH = \
    os.path.join(os.path.dirname(__file__), "agent_datasets.json")
