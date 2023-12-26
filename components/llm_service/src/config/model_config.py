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
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught
# Config dicts that hold the current config for providers, models,
# embedding models

import inspect
import json
from typing import Dict, Any, Callable, Tuple, List
from common.utils.config import get_environ_flag
from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
from common.utils.http_exceptions import InternalServerError
import langchain.chat_models as langchain_chat
import langchain.llms as langchain_llm
import langchain.embeddings as langchain_embedding

Logger = Logger.get_logger(__file__)

LANGCHAIN_CHAT_CLASSES = {
  k:klass for (k, klass) in inspect.getmembers(langchain_chat)
  if isinstance(klass, type)
}
LANGCHAIN_LLM_CLASSES = {
  k:klass() for (k, klass) in langchain_llm.get_type_to_cls_dict().items()
}
LANGCHAIN_EMBEDDING_CLASSES = {
  k:klass for (k, klass) in inspect.getmembers(langchain_embedding)
  if isinstance(klass, type)
}
LANGCHAIN_CLASSES = LANGCHAIN_CHAT_CLASSES | LANGCHAIN_LLM_CLASSES \
                    | LANGCHAIN_EMBEDDING_CLASSES

# config dict keys
KEY_ENABLED = "enabled"
KEY_MODELS = "models"
KEY_PROVIDERS = "providers"
KEY_PROVIDER = "provider"
KEY_EMBEDDINGS = "embeddings"
KEY_API_KEY = "api_key"
KEY_ENV_FLAG = "env_flag"
KEY_MODEL_CLASS = "model_class"
KEY_MODEL_NAME = "model_name"
KEY_MODEL_PARAMS = "model_params"
KEY_IS_CHAT = "is_chat"

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
  KEY_IS_CHAT
]

# providers
PROVIDER_VERTEX = "Vertex"
PROVIDER_MODEL_GARDEN = "ModelGarden"
PROVIDER_LANGCHAIN = "Langchain"
PROVIDER_TRUSS = "Truss"
PROVIDER_LLM_SERVICE = "LLMService"

# model ids
OPENAI_LLM_TYPE_GPT3_5 = "OpenAI-GPT3.5"
OPENAI_LLM_TYPE_GPT4 = "OpenAI-GPT4"
OPENAI_EMBEDDING_TYPE = "OpenAI-Embeddings"
COHERE_LLM_TYPE = "Cohere"
LLAMA2CPP_LLM_TYPE = "Llama2cpp"
LLAMA2CPP_LLM_TYPE_EMBEDDING = "Llama2cpp-Embedding"
VERTEX_LLM_TYPE_BISON_TEXT = "VertexAI-Text"
VERTEX_LLM_TYPE_BISON_V1_CHAT = "VertexAI-Chat-V1"
VERTEX_LLM_TYPE_BISON_CHAT = "VertexAI-Chat"
VERTEX_LLM_TYPE_GECKO_EMBEDDING = "VertexAI-Embedding"
VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT = "VertexAI-ModelGarden-LLAMA2-Chat"
TRUSS_LLM_LLAMA2_CHAT = "Truss-Llama2-Chat"

MODEL_TYPES = [
  OPENAI_LLM_TYPE_GPT3_5,
  OPENAI_LLM_TYPE_GPT4,
  OPENAI_EMBEDDING_TYPE,
  COHERE_LLM_TYPE,
  LLAMA2CPP_LLM_TYPE,
  LLAMA2CPP_LLM_TYPE_EMBEDDING,
  VERTEX_LLM_TYPE_BISON_TEXT,
  VERTEX_LLM_TYPE_BISON_V1_CHAT,
  VERTEX_LLM_TYPE_BISON_CHAT,
  VERTEX_LLM_TYPE_GECKO_EMBEDDING,
  VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT,
  TRUSS_LLM_LLAMA2_CHAT
]

class ModelConfigMissingException(Exception):
  pass

class ProviderConfigMissingException(Exception):
  pass

class InvalidModelConfigException(Exception):
  pass

class ModelConfig():
  """
  Model config class

  Instances of this class represent config for LLM models managed by the
  LLM Service.  Config is stored in three instance dicts:
  
  llm_model_providers: Dict[str, Dict[str, Any]] 
    provider_id: provider config dict

    provider config keys:
      enabled: is provider enabled
      env_flag: environment variable to enable/disable provider

  llm_models: Dict[str, Dict[str, Any]]
    model_id: model config dict

    model config keys:
      enabled: is model enabled
      is_chat: is the model a chat model
      provider: the provider of the model
      api_base_url: base url of a model served by an external provider
      api_key: secret id for api key

  llm_embedding_models: Dict[str, Dict[str, Any]]
    model_id: embedding model config dict
  
    embedding model config uses all model config keys
    embedding models also include these keys
      dimension: dimension of embedding vector
  """

  def __init__(self, model_config_path: str):
    self.model_config_path = model_config_path
    self.llm_model_providers: Dict[str, Dict[str, Any]] = {}
    self.llm_models: Dict[str, Dict[str, Any]] = {}
    self.llm_embedding_models: Dict[str, Dict[str, Any]] = {}

  def read_model_config(self):
    """ read model config from json config file """
    try:
      with open(self.model_config_path, "r", encoding="utf-8") as file:
        model_config = json.load(file)
        self.llm_model_providers = model_config.get(KEY_PROVIDERS, {})
        self.llm_models = model_config.get(KEY_MODELS, {})
        self.llm_embedding_models = model_config.get(KEY_EMBEDDINGS, {})
    except Exception as e:
      Logger.error(
          "Can't load models config json at"
          f" {self.model_config_path}: {str(e)}")
      raise InternalServerError(str(e)) from e

  def set_model_config(self):
    """
    Initialize and set config for providers, models and embeddings, based
    on current config dicts (loaded from a config file), environment variables
    and secrets associated with the project.
    
    This method performs the following:
    
    - Validate model config, by checking model type and keys
    
    - Set enabled flags for models.  
      A model is enabled if its config setting
      is enabled, environment variables (which override config file settings)
      are set to true if present, the provider of the model is enabled, and the
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

      # Get enabled boolean setting in model config
      model_enabled = model_config.get(KEY_ENABLED, True)

      # if there is no env flag variable for this model, or it is not set,
      # then env_flag_setting defaults to True
      env_flag_setting = True
      if KEY_ENV_FLAG in model_config:
        env_flag = model_config[KEY_ENV_FLAG]
        env_flag_setting = get_environ_flag(env_flag)

      # Validate presence of provider config and determine whether the
      # provider is enabled. By default providers are enabled. If provider
      # config is not present model is disabled.
      _, provider_config = self.get_model_provider_config(model_id)
      if provider_config is None:
        Logger.error(
            f"Provider config for model {model_id} not found: disabling")
        model_config[KEY_ENABLED] = False
        continue
      provider_enabled = provider_config.get(KEY_ENABLED, True)

      # Get api keys if present. If an api key serect is configured and
      # the key is missing, disable the model.
      api_key = self.get_api_key(model_id)
      api_check = True
      if self.get_config_value(model_id, KEY_API_KEY):
        api_check = api_key is not None

      model_enabled = \
          api_check and \
          model_enabled and \
          provider_enabled and \
          env_flag_setting

      model_config[KEY_ENABLED] = model_enabled

      # instantiate model class if necessary (mainly langchain models)
      if model_enabled and KEY_MODEL_CLASS in model_config:
        model_instance = self.instantiate_model_class(model_id)
        model_config[KEY_MODEL_CLASS] = model_instance

      Logger.info(
          f"Setting model enabled flag for {model_id} to {model_enabled}")

  def is_model_enabled(self, model_id: str) -> bool:
    """
    Get model enabled setting.  We default to true if there is no key
    present, so users must set the enable flag = false in config if that is
    the desired behavior.
    """
    model_config = self.get_model_config(model_id)
    return model_config.get(KEY_ENABLED, True)

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

  def is_provider_enabled(self, provider_id: str) -> bool:
    """ return provider enabled setting """
    provider_config = self.get_provider_config(provider_id, None)
    if provider_config is None:
      raise ProviderConfigMissingException(provider_id)
    return provider_config.get(KEY_ENABLED, True)

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

  def get_provider_config(self, provider_id: str, default=None) -> dict:
    """ get provider config for provider """
    return self.llm_model_providers.get(provider_id, default)

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
      provider_config = self.get_provider_config(provider, None)
    return provider, provider_config

  def get_config_value(self, model_id: str, key: str) -> Any:
    return self.get_model_config(model_id).get(key)

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
      # get the key secret id from config
      api_key_id = model_config.get(KEY_API_KEY, None)
      if api_key_id:
        # if there is a secret id in config get the key from secrets
        try:
          api_key = get_secret(api_key_id)
        except Exception as e:
          # Failing to retrieve the key should be a non-fatal error -
          # it should normally just result in the model being disabled.
          # Here we will just log an error.
          Logger.error(
              f"Unable to get api key secret {api_key_id} "
              f"for {model_id}: {str(e)}")

    model_config["api_key_value"] = api_key
    return api_key

  def instantiate_model_class(self, model_id: str) -> Callable:
    """ 
    Instantiate the model class for providers that use them (e.g. Langchain)
    """
    model_class_instance = None
    provider, _ = self.get_model_provider_config(model_id)
    model_class_name = self.get_config_value(model_id, KEY_MODEL_CLASS)
    model_name = self.get_config_value(model_id, KEY_MODEL_NAME)
    model_params = self.get_config_value(model_id, KEY_MODEL_PARAMS)
    if model_params is None:
      model_params = {}
    if provider == PROVIDER_LANGCHAIN:
      model_cls = LANGCHAIN_CLASSES.get(model_class_name)
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
