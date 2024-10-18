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
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught,unused-import
import os
import json
from common.config import REGION
from common.utils.config import get_environ_flag, load_config_json
from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
from common.utils.gcs_adapter import get_blob_from_gcs_path
from common.utils.token_handler import UserCredentials
from schemas.error_schema import (UnauthorizedResponseModel,
                                  InternalServerErrorResponseModel,
                                  ValidationErrorResponseModel)
from google.cloud import secretmanager
from config.model_config import (ModelConfig, VENDOR_OPENAI,
                                PROVIDER_VERTEX, VENDOR_COHERE,
                                PROVIDER_LANGCHAIN, PROVIDER_MODEL_GARDEN,
                                PROVIDER_TRUSS, PROVIDER_LLM_SERVICE,
                                PROVIDER_VLLM, VLLM_LLM_GEMMA_CHAT,
                                VERTEX_LLM_TYPE_CHAT,
                                VERTEX_LLM_TYPE_BISON_CHAT, TRUSS_LLM_LLAMA2_CHAT,
                                VERTEX_LLM_TYPE_GECKO_EMBEDDING,
                                VERTEX_LLM_TYPE_GECKO_EMBEDDING_VISION,
                                VERTEX_LLM_TYPE_GEMINI_PRO,
                                VERTEX_LLM_TYPE_GEMINI_PRO_VISION,
                                VERTEX_LLM_TYPE_GEMINI_FLASH)

Logger = Logger.get_logger(__file__)
secrets = secretmanager.SecretManagerServiceClient()

PORT = os.environ["PORT"] if os.environ.get("PORT") is not None else 80
PROJECT_ID = os.environ.get("PROJECT_ID")
assert PROJECT_ID, "PROJECT_ID must be set"

os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
GCP_PROJECT = PROJECT_ID
DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")

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

PAYLOAD_FILE_SIZE = 100000000

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

# model config
_model_config = None
MODEL_CONFIG_PATH = None

def get_model_config() -> ModelConfig:
  global _model_config
  global MODEL_CONFIG_PATH
  if _model_config is None:
    MODEL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "models.json")
    _model_config = ModelConfig(MODEL_CONFIG_PATH)
    _model_config.load_model_config()
  return _model_config

mc = get_model_config()

# provider enabled flags
ENABLE_GOOGLE_LLM = mc.is_provider_enabled(PROVIDER_VERTEX)
ENABLE_GOOGLE_MODEL_GARDEN = \
    mc.is_provider_enabled(PROVIDER_MODEL_GARDEN)
ENABLE_TRUSS_LLAMA2 = mc.is_provider_enabled(PROVIDER_TRUSS)
ENABLE_VLLM_GEMMA = mc.is_provider_enabled(PROVIDER_VLLM)

# vendor enabled flags
ENABLE_OPENAI_LLM = mc.is_vendor_enabled(VENDOR_OPENAI)
ENABLE_COHERE_LLM = mc.is_vendor_enabled(VENDOR_COHERE)

Logger.info(f"ENABLE_GOOGLE_LLM = {ENABLE_GOOGLE_LLM}")
Logger.info(f"ENABLE_OPENAI_LLM = {ENABLE_OPENAI_LLM}")
Logger.info(f"ENABLE_COHERE_LLM = {ENABLE_COHERE_LLM}")
Logger.info(f"ENABLE_GOOGLE_MODEL_GARDEN = {ENABLE_GOOGLE_MODEL_GARDEN}")
Logger.info(f"ENABLE_TRUSS_LLAMA2 = {ENABLE_TRUSS_LLAMA2}")
Logger.info(f"ENABLE_VLLM_GEMMA = {ENABLE_VLLM_GEMMA}")

# API Keys
_, OPENAI_API_KEY = mc.get_vendor_api_key(VENDOR_OPENAI)
_, COHERE_API_KEY = mc.get_vendor_api_key(VENDOR_COHERE)

# default models
DEFAULT_LLM_TYPE = VERTEX_LLM_TYPE_CHAT
DEFAULT_CHAT_LLM_TYPE = VERTEX_LLM_TYPE_CHAT
DEFAULT_MULTI_LLM_TYPE = VERTEX_LLM_TYPE_GEMINI_FLASH
DEFAULT_QUERY_CHAT_MODEL = VERTEX_LLM_TYPE_GEMINI_FLASH
DEFAULT_QUERY_EMBEDDING_MODEL = VERTEX_LLM_TYPE_GECKO_EMBEDDING
DEFAULT_QUERY_MULTI_EMBEDDING_MODEL = VERTEX_LLM_TYPE_GECKO_EMBEDDING_VISION

# other defaults
DEFAULT_WEB_DEPTH_LIMIT = 1

# config for agents and datasets
AGENT_CONFIG_PATH = os.environ.get("AGENT_CONFIG_PATH")
if not AGENT_CONFIG_PATH:
  AGENT_CONFIG_PATH = os.path.join(
      os.path.dirname(__file__), "agent_config.json")

DATASETS = None
AGENTS = None

def get_dataset_config() -> dict:
  return DATASETS

def get_agent_config() -> dict:
  global AGENTS
  global DATASETS
  if AGENTS is None:
    if AGENT_CONFIG_PATH[:5] == "gs://":
      blob = get_blob_from_gcs_path(AGENT_CONFIG_PATH)
      agent_config = json.loads(blob.download_as_string())
    else:
      agent_config = load_config_json(AGENT_CONFIG_PATH)
    if "Agents" in agent_config:
      AGENTS = agent_config["Agents"]
    else:
      raise RuntimeError("invalid agent config")
    if "Datasets" in agent_config:
      DATASETS = agent_config["Datasets"]
    else:
      DATASETS = {}
  return AGENTS

# load agent config
get_agent_config()

# document manifest config
DEFAULT_DOCUMENT_MANIFEST = None
def get_default_manifest() -> dict:
  return DEFAULT_DOCUMENT_MANIFEST

DEFAULT_DOCUMENT_MANIFEST_PATH = \
    os.environ.get("DEFAULT_DOCUMENT_MANIFEST_PATH")
if not DEFAULT_DOCUMENT_MANIFEST_PATH:
  DEFAULT_DOCUMENT_MANIFEST_PATH = os.path.join(
      os.path.dirname(__file__), "document_manifest.json")
  try:
    default_manifest = load_config_json(DEFAULT_DOCUMENT_MANIFEST_PATH)
    Logger.info(
        f"Loaded default manifest from {DEFAULT_DOCUMENT_MANIFEST_PATH}")
    DEFAULT_DOCUMENT_MANIFEST = default_manifest
  except Exception:
    Logger.info("Unable to load default manifest")

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
