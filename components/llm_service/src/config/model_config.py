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
  LLM Service config object module
"""
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught,protected-access
# Config dicts that hold the current config for providers, models,
# embedding models

import importlib
import inspect
import json
import os
from pathlib import Path
from typing import Dict, Any, Callable, Tuple, List
from common.utils.config import get_environ_flag
from common.utils.gcs_adapter import download_file_from_gcs
from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
import langchain_community.chat_models as langchain_chat
import langchain_community.llms as langchain_llm
import langchain_community.embeddings as langchain_embedding
from langchain_google_vertexai import ChatVertexAI
from langchain_openai import ChatOpenAI

Logger = Logger.get_logger(__file__)

# config dict keys
KEY_ENABLED = "enabled"
KEY_MODELS = "models"
KEY_PROVIDERS = "providers"
KEY_VENDORS = "vendors"
KEY_PROVIDER = "provider"
KEY_EMBEDDINGS = "embeddings"
KEY_API_KEY = "api_key"
KEY_ENV_FLAG = "env_flag"
KEY_MODEL_CLASS = "model_class"
KEY_MODEL_NAME = "model_name"
KEY_MODEL_PARAMS = "model_params"
KEY_MODEL_CONTEXT_LENGTH = "context_length"
KEY_IS_CHAT = "is_chat"
KEY_IS_MULTI = "is_multi"
KEY_MODEL_FILE_URL = "model_file_url"
KEY_MODEL_PATH = "model_path"
KEY_MODEL_ENDPOINT = "model_endpoint"
KEY_VENDOR = "vendor"
KEY_DIMENSION = "dimension"

MODEL_CONFIG_KEYS = [
  KEY_ENABLED,
  KEY_MODELS,
  KEY_PROVIDERS,
  KEY_PROVIDER,
  KEY_EMBEDDINGS,
  KEY_API_KEY,
  KEY_ENV_FLAG,
  KEY_MODEL_CLASS,
  KEY_MODEL_NAME,
  KEY_MODEL_PARAMS,
  KEY_MODEL_CONTEXT_LENGTH,
  KEY_IS_CHAT,
  KEY_IS_MULTI,
  KEY_MODEL_FILE_URL,
  KEY_MODEL_PATH,
  KEY_MODEL_ENDPOINT,
  KEY_VENDOR,
  KEY_DIMENSION
]

# model providers
PROVIDER_VERTEX = "Vertex"
PROVIDER_MODEL_GARDEN = "ModelGarden"
PROVIDER_LANGCHAIN = "Langchain"
PROVIDER_TRUSS = "Truss"
PROVIDER_VLLM = "vLLM"
PROVIDER_LLM_SERVICE = "LLMService"

# model vendors
VENDOR_OPENAI = "OpenAI"
VENDOR_COHERE = "Cohere"

# model ids
OPENAI_LLM_TYPE_GPT3_5 = "OpenAI-GPT3.5"
OPENAI_LLM_TYPE_GPT4 = "OpenAI-GPT4"
OPENAI_LLM_TYPE_GPT4_LATEST = "OpenAI-GPT4-latest"
OPENAI_EMBEDDING_TYPE = "OpenAI-Embedding"
COHERE_LLM_TYPE = "Cohere"
LLAMA2CPP_LLM_TYPE = "Llama2cpp"
LLAMA2CPP_LLM_TYPE_EMBEDDING = "Llama2cpp-Embedding"
VERTEX_LLM_TYPE_CHAT = "VertexAI-Chat"
VERTEX_LLM_TYPE_BISON_TEXT = "VertexAI-Text"
VERTEX_LLM_TYPE_BISON_CHAT = "VertexAI-Chat-Palm2"
VERTEX_LLM_TYPE_BISON_V1_CHAT = "VertexAI-Chat-V1"
VERTEX_LLM_TYPE_BISON_V2_CHAT = "VertexAI-Chat-Palm2-V2"
VERTEX_LLM_TYPE_BISON_CHAT_32K = "VertexAI-Chat-Palm2-32k"
VERTEX_LLM_TYPE_GECKO_EMBEDDING = "VertexAI-Embedding"
VERTEX_LLM_TYPE_GECKO_EMBEDDING_VISION = "VertexAI-Embedding-Vision"
VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT = "VertexAI-ModelGarden-LLAMA2-Chat"
TRUSS_LLM_LLAMA2_CHAT = "Truss-Llama2-Chat"
VLLM_LLM_GEMMA_CHAT = "vLLM-Gemma-Chat"
VERTEX_LLM_TYPE_BISON_CHAT_LANGCHAIN = "VertexAI-Chat-Palm2V2-Langchain"
VERTEX_LLM_TYPE_BISON_CHAT_32K_LANGCHAIN = "VertexAI-Chat-Palm2-32k-Langchain"
VERTEX_LLM_TYPE_GEMINI_PRO = "VertexAI-Gemini-Pro"
VERTEX_LLM_TYPE_GEMINI_PRO_VISION = "VertexAI-Gemini-Pro-Vision"
VERTEX_LLM_TYPE_GEMINI_PRO_LANGCHAIN = "VertexAI-Chat-Gemini-Pro-Langchain"
HUGGINGFACE_EMBEDDING = "HuggingFaceEmbeddings"

MODEL_TYPES = [
  VERTEX_LLM_TYPE_CHAT,
  OPENAI_LLM_TYPE_GPT3_5,
  OPENAI_LLM_TYPE_GPT4,
  OPENAI_LLM_TYPE_GPT4_LATEST,
  OPENAI_EMBEDDING_TYPE,
  COHERE_LLM_TYPE,
  LLAMA2CPP_LLM_TYPE,
  LLAMA2CPP_LLM_TYPE_EMBEDDING,
  VERTEX_LLM_TYPE_BISON_TEXT,
  VERTEX_LLM_TYPE_BISON_CHAT,
  VERTEX_LLM_TYPE_BISON_V2_CHAT,
  VERTEX_LLM_TYPE_BISON_V1_CHAT,
  VERTEX_LLM_TYPE_GEMINI_PRO,
  VERTEX_LLM_TYPE_GEMINI_PRO_VISION,
  VERTEX_LLM_TYPE_GECKO_EMBEDDING,
  VERTEX_LLM_TYPE_GECKO_EMBEDDING_VISION,
  VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT,
  TRUSS_LLM_LLAMA2_CHAT,
  VLLM_LLM_GEMMA_CHAT,
  VERTEX_LLM_TYPE_BISON_CHAT_LANGCHAIN,
  VERTEX_LLM_TYPE_BISON_CHAT_32K,
  VERTEX_LLM_TYPE_BISON_CHAT_32K_LANGCHAIN,
  VERTEX_LLM_TYPE_GEMINI_PRO_LANGCHAIN,
  HUGGINGFACE_EMBEDDING
]

class ModelConfigMissingException(Exception):
  def __init__(self, key):
    self.message = f"Model config missing for {key}."
    super().__init__(self.message)

class InvalidModelConfigException(Exception):
  def __init__(self, message):
    self.message = message
    super().__init__(self.message)

def load_langchain_classes() -> dict:
  """
  Load langchain classes.  Return a dict mapping classname to 
  class instance.  The langchain version nightmare makes this step
  particularly challenging to maintain.
  """
  langchain_chat_classes = {
    k:getattr(importlib.import_module(klass), k)
    for k,klass in langchain_chat._module_lookup.items()
  }
  langchain_llm_classes = {
    klass().__name__:klass()
    for klass in langchain_llm.get_type_to_cls_dict().values()
  }
  if hasattr(langchain_embedding, "_module_lookup"):
    langchain_embedding_classes = {
      k:getattr(importlib.import_module(klass), k)
      for k,klass in langchain_embedding._module_lookup.items()
    }
  else:
    langchain_embedding_classes = {
      k:klass for (k, klass) in inspect.getmembers(langchain_embedding)
      if isinstance(klass, type)
    }

  # special handling for Vertex and OpenAI chat models, which are
  # imported in community packages
  langchain_chat_classes["ChatOpenAI"] = ChatOpenAI
  langchain_chat_classes["ChatVertexAI"] = ChatVertexAI

  langchain_classes = langchain_chat_classes | langchain_llm_classes \
                      | langchain_embedding_classes

  return langchain_classes

class ModelConfig():
  """
  Model config class

  Instances of this class represent config for LLM models managed by the
  LLM Service.  Config is stored in four instance dicts:

  llm_model_providers: Dict[str, Dict[str, Any]]
    { ...
      provider_id: {
        {
          ...
          provider config key: value
        }
    }

    provider config keys:
      enabled: is provider enabled
      env_flag: environment variable to enable/disable provider
      model_params: global provider generation parameters

  llm_model_vendors: Dict[str, Dict[str, Any]]
    { ...
      vendor_id: {
        ...
        vendor config key: value
      }
    }

    vendor config keys:
      enabled: is vendor enabled
      env_flag: environment variable to enable/disable vendor
      api_key: secret id for api key
      model_params: global vendor generation parameters

  llm_models: Dict[str, Dict[str, Any]]
    { ...
      model_id: {
        ...
        model config key: value
      }
    }
    model config keys:
      enabled: is model enabled
      is_chat: is the model a chat model
      provider: the provider of the model
      model_endpoint: base url of a model served by an external provider
      model_class: class to instantiate for model, e.g. langchain model class
      model_params: generation parameters
      vendor: vendor id
      env_flag: environment variable to enable/disable model
      model_file_url: url of model file to load

  llm_embedding_models: Dict[str, Dict[str, Any]]
    { ...
      model_id: {
        ...
        embedding model config key: value
      }
    }

    embedding model config uses all model config keys except is_chat
    embedding models also include these keys
      dimension: dimension of embedding vector
  """

  def __init__(self, model_config_path: str):
    self.model_config_path = model_config_path
    self.llm_model_providers: Dict[str, Dict[str, Any]] = {}
    self.llm_model_vendors: Dict[str, Dict[str, Any]] = {}
    self.llm_models: Dict[str, Dict[str, Any]] = {}
    self.llm_embedding_models: Dict[str, Dict[str, Any]] = {}

  def read_model_config(self):
    """ read model config from json config file """
    try:
      with open(self.model_config_path, "r", encoding="utf-8") as file:
        model_config = json.load(file)
        self.llm_model_providers = model_config.get(KEY_PROVIDERS, {})
        self.llm_model_vendors = model_config.get(KEY_VENDORS, {})
        self.llm_models = model_config.get(KEY_MODELS, {})
        self.llm_embedding_models = model_config.get(KEY_EMBEDDINGS, {})
    except Exception as e:
      Logger.error(
          "Can't load models config json at"
          f" {self.model_config_path}: {str(e)}")
      raise RuntimeError(str(e)) from e

  def copy_model_config(self, mc):
    """ copy model config from another config object """
    self.model_config_path = mc.model_config_path
    self.llm_model_providers = mc.llm_model_providers
    self.llm_model_vendors = mc.llm_model_vendors
    self.llm_models = mc.llm_models
    self.llm_embedding_models = mc.llm_embedding_models

  def set_model_config(self):
    """
    Initialize and set config for providers, models and embeddings, based
    on current config dicts (loaded from a config file), environment variables
    and secrets associated with the project.

    This method performs the following:

    - Validate model config, by checking model type and keys

    - Set enabled flags for models.
      A model is enabled if its config setting is enabled, environment
      variables (which override config file settings) are set to true if
      present, the provider of the model is enabled, and the
      API key is present (if applicable).

    - Set API keys for models.

    - Instantiate model classes and store in the config dicts for models and
    Embeddings.

    We always default to True if a setting or env var is not present.
    """
    for model_id, model_config in self.get_all_model_config().items():
      # validate model config
      if model_id not in MODEL_TYPES:
        raise InvalidModelConfigException(f"{model_id} not in MODEL_TYPES")

      # check keys
      for key in model_config.keys():
        if key not in MODEL_CONFIG_KEYS:
          raise InvalidModelConfigException(
              f"Invalid key {key} in {model_config}")

      # Get model enabled boolean setting in model config and env vars
      model_enabled = self.is_model_enabled(model_id)

      # Get vendor enabled setting in config and env vars
      vendor_id, _ = self.get_model_vendor_config(model_id)
      vendor_enabled = self.is_vendor_enabled(vendor_id)

      # Validate presence of provider config and determine whether the
      # provider is enabled. By default providers are enabled. If provider
      # config is not present model is disabled.
      provider_id, provider_config = self.get_model_provider_config(model_id)
      if provider_config is None:
        Logger.error(
            f"Provider config for model {model_id} not found: disabling")
        model_config[KEY_ENABLED] = False
        continue
      provider_enabled = self.is_provider_enabled(provider_id)

      # Get api keys if present. If an api key secret is configured and
      # the key is missing, disable the model.
      api_key = self.get_api_key(model_id)
      api_check = True
      if self.get_config_value(model_id, KEY_API_KEY):
        api_check = api_key is not None

      # set model_enabled flag based on conjunction of settings
      model_enabled = \
          model_enabled and \
          api_check and \
          provider_enabled and \
          vendor_enabled

      model_config[KEY_ENABLED] = model_enabled

      # instantiate model class if necessary (mainly langchain models)
      if model_enabled and KEY_MODEL_CLASS in model_config:
        model_instance = self.instantiate_model_class(model_id)
        if model_instance is None:
          Logger.warning(f"Disabling model {model_id}")
          model_config[KEY_ENABLED] = False
        model_config[KEY_MODEL_CLASS] = model_instance

      # download model file if necessary
      if KEY_MODEL_FILE_URL in model_config and model_enabled:
        self.download_model_file(model_id, model_config)

  def is_model_enabled(self, model_id: str) -> bool:
    """
    Get model enabled setting.  We default to true if there is no key
    present, so users must set the enable flag = false in config if that is
    the desired behavior.
    """
    model_config = self.get_model_config(model_id)

    # check env flag if present
    model_flag_setting = True
    if KEY_ENV_FLAG in model_config:
      env_flag = model_config[KEY_ENV_FLAG]
      model_flag_setting = get_environ_flag(env_flag)

    # check enabled config key
    model_key_enabled = model_config.get(KEY_ENABLED, True)

    # provider enabled if config and env flag are true
    model_enabled = model_key_enabled and model_flag_setting

    return model_enabled

  def get_model_config(self, model_id: str) -> dict:
    """
    Get model config, for any model (llm or embedding).
    It is an error if the model config is missing for model_id, so raise an
    exception if so.
    """
    model_config = self.get_all_model_config().get(model_id, None)
    if model_config is None:
      raise ModelConfigMissingException(model_id)
    return model_config

  # providers

  def is_provider_enabled(self, provider_id: str) -> bool:
    """ return provider enabled setting """
    provider_config = self.get_provider_config(provider_id)
    if provider_config is None:
      raise ModelConfigMissingException(provider_id)

    # check provider enable env flag
    provider_flag_setting = True
    if KEY_ENV_FLAG in provider_config:
      env_flag = provider_config[KEY_ENV_FLAG]
      provider_flag_setting = get_environ_flag(env_flag)

    # check enabled config key
    provider_key_enabled = provider_config.get(KEY_ENABLED, True)

    # provider enabled if config and env flag are true
    provider_enabled = provider_key_enabled and provider_flag_setting

    return provider_enabled

  def get_provider_llm_types(self, provider_id: str) -> List[str]:
    """ Get list of model ids (llm only, not embedding) for provider LLMs """
    provider_llms = [
      model_id for model_id, model_config in self.llm_models.items()
      if model_config.get(KEY_PROVIDER) == provider_id
    ]
    return provider_llms

  def get_provider_embedding_types(self, provider_id: str) -> List[str]:
    provider_embeddings = [
      model_id for model_id, model_config in self.llm_embedding_models.items()
      if model_config.get(KEY_PROVIDER) == provider_id
    ]
    return provider_embeddings

  def get_provider_config(self, provider_id: str) -> dict:
    """ get provider config for provider """
    return self.llm_model_providers.get(provider_id, None)

  def get_model_provider_config(self, model_id: str) -> Tuple[str, dict]:
    """
    Get provider config for model.
    Args:
      model_id: model id
    Returns:
      tuple of provider id, config
    """
    provider_config = None
    model_config = self.get_model_config(model_id)
    provider = model_config.get(KEY_PROVIDER, None)
    if provider is not None:
      provider_config = self.get_provider_config(provider)
      Logger.info(f"provider = {provider}")
      Logger.info(f"provider_config = {provider_config}")
    return provider, provider_config

  def get_provider_models(self, provider_id: str) -> List[str]:
    """ return list of model ids for provider """
    provider_models = [
      model_id
      for model_id, _ in self.get_all_model_config().items()
      if self.get_config_value(model_id, KEY_PROVIDER) == provider_id
    ]
    return provider_models

  def get_provider_model_config(self, provider_id: str) -> dict:
    """ get model config dict for provider models """
    provider_model_config = {
      model_id: model_config
      for model_id, model_config in self.get_all_model_config().items()
      if self.get_config_value(model_id, KEY_PROVIDER) == provider_id
    }
    return provider_model_config

  def get_provider_value(self, provider_id: str, key: str,
                         model_id: str = None, default=None) -> Any:
    """ get config value from provider model config """

    Logger.info("Get provider value:")
    Logger.info(f"provider_id={provider_id}")
    Logger.info(f"model_id={model_id}")

    if model_id is None:
      # get global provider value
      provider_config = self.get_provider_config(provider_id)
      value = provider_config.get(key, default)
    else:
      provider_config = self.get_provider_model_config(provider_id)
      Logger.debug(f"provider_config={provider_config}")
      model_config = provider_config.get(model_id)
      value = model_config.get(key, default)

    if value is None:
      Logger.error(f"key {key} for provider {provider_id} is None")
    return value

  # vendors

  def is_vendor_enabled(self, vendor_id: str) -> bool:
    """ return vendor enabled setting """
    vendor_config = self.get_vendor_config(vendor_id)

    # if vendor config is missing assume vendor is enabled
    if vendor_config is None:
      return True

    vendor_flag_setting = True
    if KEY_ENV_FLAG in vendor_config:
      env_flag = vendor_config[KEY_ENV_FLAG]
      vendor_flag_setting = get_environ_flag(env_flag)

    # check enabled config key
    vendor_key_enabled = vendor_config.get(KEY_ENABLED, True)

    # provider enabled if config and env flag are true
    vendor_enabled = vendor_key_enabled and vendor_flag_setting

    return vendor_enabled

  def get_model_vendor_config(self, model_id: str) -> dict:
    """
    Get vendor config for model.
    Args:
      model_id: model id
    Returns:
      tuple of vendor id, config
    """
    vendor_config = None
    model_config = self.get_model_config(model_id)
    vendor_id = model_config.get(KEY_VENDOR, None)
    if vendor_id is not None:
      vendor_config = self.get_vendor_config(vendor_id)
    return vendor_id, vendor_config

  def get_vendor_config(self, vendor_id: str) -> dict:
    return self.llm_model_vendors.get(vendor_id, None)

  def get_vendor_api_key(self, vendor_id: str) -> Tuple[str, str]:
    """ get vendor API key name and value """
    api_key = None
    api_key_name = None
    vendor_config = self.get_vendor_config(vendor_id)
    if vendor_config is not None:
      api_key_name = vendor_config.get(KEY_API_KEY)
      if api_key_name:
        # if there is a secret id in config get the key from secrets
        try:
          api_key = get_secret(api_key_name)
        except Exception as e:
          # Failing to retrieve the key should be a non-fatal error -
          # it should normally just result in the model being disabled.
          # Here we will just log an error.
          Logger.error(
              f"Unable to get api key secret {api_key_name} "
              f"for {vendor_id}: {str(e)}")

        # return the name in proper format as a param name
        api_key_name = api_key_name.replace("-", "_")
    return api_key_name, api_key

  def get_config_value(self, model_id: str, key: str, default=None) -> Any:
    return self.get_model_config(model_id).get(key, default)

  def get_all_model_config(self):
    """ return dict of model config and embedding model config combined """
    model_config = self.llm_models.copy()
    model_config.update(self.llm_embedding_models)
    return model_config

  def get_api_keys(self) -> dict:
    """ return a dict of model_id: api_key """
    api_keys = {}
    for model_id, _ in self.get_all_model_config().items():
      api_key = self.get_api_key(model_id)
      api_keys.update({model_id: api_key})
    return api_keys

  def get_api_key(self, model_id: str) -> str:
    """ Get api key for model.  Also set it into model config. """
    model_config = self.get_model_config(model_id)
    api_key = None
    if self.is_model_enabled(model_id):
      # if vendor config exists retrieve api key
      vendor_id, vendor_config = self.get_model_vendor_config(model_id)
      if vendor_config is not None:
        _, api_key = self.get_vendor_api_key(vendor_id)
        if api_key is None:
          # log error if vendor is configured for model but api key not found
          Logger.error(f"Unable to get api key for {model_id} ")

    model_config[KEY_API_KEY] = api_key
    return api_key

  def instantiate_model_class(self, model_id: str) -> Callable:
    """
    Instantiate the model class for providers that use them (e.g. Langchain)
    """
    langchain_classes = load_langchain_classes()
    model_class_instance = None
    provider, _ = self.get_model_provider_config(model_id)
    model_class_name = self.get_config_value(model_id, KEY_MODEL_CLASS)
    model_name = self.get_config_value(model_id, KEY_MODEL_NAME)
    model_params = self.get_config_value(model_id, KEY_MODEL_PARAMS)

    if model_params is None:
      model_params = {}
    if provider == PROVIDER_LANGCHAIN:
      vendor_id, vendor_config = self.get_model_vendor_config(model_id)
      if vendor_config is not None:
        # get api key name and value for model vendor
        api_key_name, api_key = self.get_vendor_api_key(vendor_id)

        # add api key to model params
        model_params.update({api_key_name: api_key})

      # retrieve and instantiate langchain model class
      model_cls = langchain_classes.get(model_class_name, None)
      if model_cls is None:
        Logger.error(f"Cannot load langchain model class {model_class_name}")
        model_class_instance = None
      elif model_name is None:
        model_class_instance = model_cls(**model_params)
      else:
        model_class_instance = model_cls(model_name=model_name, **model_params)
    return model_class_instance

  def load_model_config(self):
    """
    Load model config dicts.
    Refresh api keys and set enabled flags for all models.
    """
    self.read_model_config()
    self.set_model_config()

  def get_llm_types(self) -> dict:
    """ Get all supported and enabled LLM types, as a list of model
        identifiers.
    """
    llm_configured_types = self.llm_models.keys()
    llm_types = [
      llm for llm in llm_configured_types if self.is_model_enabled(llm)
    ]
    return llm_types

  def get_chat_llm_types(self) -> dict:
    """ Get all supported and enabled chat LLM types, as a list of model
        identifiers.
    """
    chat_llm_types = [
      m for m,config in self.llm_models.items()
      if (KEY_IS_CHAT in config and config[KEY_IS_CHAT]) and self.is_model_enabled(m)
    ]
    return chat_llm_types

  def get_multi_llm_types(self) -> dict:
    """ Get all supported and enabled multimodal LLM types, as a list of model
        identifiers.
    """
    multi_llm_types = [
      m for m,config in self.llm_models.items()
      if (KEY_IS_MULTI in config and config[KEY_IS_MULTI]) and self.is_model_enabled(m)
    ]
    return multi_llm_types

  def get_embedding_types(self) -> dict:
    """ Get all supported and enabled embedding types, as a list of model
        identifiers.
    """
    embedding_types = [
      m for m,config in self.llm_embedding_models.items()
      if self.is_model_enabled(m)
    ]
    return embedding_types

  def download_model_file(self, model_id: str, model_config: dict):
    """
    Download model file for model.
    Args:
      model_id: model identifier
      model_config: model config dict

    Raises:
      RuntimeError if model download fails
      InvalidModelConfigException if config is invalid/missing
    """
    model_file_url = model_config.get(KEY_MODEL_FILE_URL, None)
    Logger.info(f"{model_id} model file url = {model_file_url}")
    model_file = Path(model_file_url).name
    models_dir = os.path.join(os.path.dirname(__file__), "models/")
    model_file_path = os.path.join(models_dir, model_file)
    Logger.info(f"{model_id} model file = {model_file_path}")
    try:
      if model_file_url.startswith("gs://"):
        # download model file from GCS
        Logger.info(f"downloading {model_id} from model file url {model_file_url}")
        model_file_path = \
            download_file_from_gcs(model_file_url,
                                   destination_folder_path=models_dir)
      elif model_file_url.startswith("file://"):
        model_file_path = model_file_url
        if not os.path.exists(model_file_path):
          raise RuntimeError(
              "{model_id} model file not present at {model_file_path}")
        model_file_path = Path(model_file_url).path
      else:
        raise InvalidModelConfigException("Invalid model url {model_file_url}")
    except Exception as e:
      raise RuntimeError(
          f"Failed to download model file {str(e)}") from e

    # set model file path in model params
    model_params = self.get_config_value(model_id, KEY_MODEL_PARAMS)
    if model_params is None:
      model_params = {}
    model_params[KEY_MODEL_PATH] = model_file_path
