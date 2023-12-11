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
  LLM Service config helper module
"""
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught
# Config dicts that hold the current config for providers, models,
# embedding models

import json
from typing import Dict, Any, Callable
from common.utils.config import get_environ_flag, get_flag_value
from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
from common.utils.http_exceptions import InternalServerError

Logger = Logger.get_logger(__file__)

# config dict keys
KEY_ENABLED = "enabled"
KEY_MODELS = "models"
KEY_PROVIDERS = "providers"
KEY_PROVIDER = "provider"
KEY_EMBEDDINGS = "embeddings"
KEY_API_KEY = "api_key"
KEY_ENV_FLAG = "env_flag"
KEY_MODEL_CLASS = "model_class"

class ModelConfigMissingException(Exception):
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
      # Get enabled boolean setting in model config
      model_enabled = get_flag_value(model_config, KEY_ENABLED)

      # if there is no env flag variable for this model, or it is not set,
      # then env_flag_setting defaults to True
      env_flag_setting = True
      if KEY_ENV_FLAG in model_config:
        env_flag = model_config[KEY_ENV_FLAG]
        env_flag_setting = get_environ_flag(env_flag)

      # Validate presence of provider config and determine whether the
      # provider is enabled. By default providers are enabled. If provider
      # config is not present model is disabled.
      provider = model_config.get(KEY_PROVIDER, None)
      if provider is None:
        Logger.error(f"No provider for model {model_id}: disabling")
        model_config[KEY_ENABLED] = False
        continue
      provider_config = self.llm_model_providers.get(provider, None)
      if provider_config is None:
        Logger.error(
            f"Provider config for model {model_id} not found: disabling")
        model_config[KEY_ENABLED] = False
        continue
      provider_enabled = get_flag_value(provider_config, KEY_ENABLED)

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

      # instantiate model class
      if model_enabled:
        model_class = self.instantiate_model_class(model_config)
        model_config[KEY_MODEL_CLASS] = model_class

      Logger.info(
          f"Setting model enabled flag for {model_id} to {model_enabled}")

  def is_model_enabled(self, model_id: str) -> bool:
    model_config = self.llm_models.get(model_id)
    return model_config(KEY_ENABLED)

  def get_model_config(self, model_id: str) -> dict:
    model_config = self.get_all_model_config().get(model_id, None)
    if model_config is None:
      raise ModelConfigMissingException(model_id)
    return model_config

  def get_config_value(self, model_id: str, key: str) -> Any:
    return self.get_model_config(model_id).get(key)

  def get_all_model_config(self):
    """ return dict of model config and embedding model config combined """
    return self.llm_models.copy().update(self.llm_embedding_models)

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

  def instantiate_model_class(self, model_config: str) -> Callable:
    """ 
    Instantiate the model class for providers that use them (e.g. Langchain)
    """
    return None

  def load_model_config(self):
    """ 
    Load model config dicts.  
    Refresh api keys and set enabled flags for all models.
    """
    self.read_model_config()
    self.set_model_config()
