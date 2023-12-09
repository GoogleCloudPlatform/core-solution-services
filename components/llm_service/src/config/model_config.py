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


# config dict keys
KEY_ENABLED = "enabled"
KEY_MODELS = "models"
KEY_PROVIDERS = "providers"
KEY_PROVIDER = "provider"
KEY_EMBEDDINGS = "embeddings"
KEY_API_KEY = "api_key"

class ModelConfigMissingException(Exception):
  pass

class ModelConfig():
  """
  Model config class
  """

  LLM_MODEL_PROVIDERS = {}
  LLM_MODELS = {}
  LLM_EMBEDDING_MODELS = {}

  def __init__(model_config_path: str):
    self.model_config_path = model_config_path

  def read_model_config(self):
    """ read model config from json config file """
    try:
      with open(self.model_config_path, "r", encoding="utf-8") as file:
        model_config = json.load(file)

      LLM_MODEL_PROVIDERS = model_config.get(KEY_PROVIDERS, LLM_MODEL_PROVIDERS)
      LLM_MODELS = model_config.get(KEY_MODELS, LLM_MODELS)
      LLM_EMBEDDING_MODELS = model_config.get(KEY_EMBEDDINGS,
          LLM_EMBEDDING_MODELS)

    except Exception as e:
      Logger.error(f"Can't load llm_service_models.json: {str(e)}")
      raise InternalServerError(str(e)) from e

  def set_model_config(self):
    """
    Set enabled flags for models.  A model is enabled if its config setting
    is enabled, environment variables (which override config file settings)
    are set to true if present, the provider of the model is enabled, and the
    API key is present (if applicable).

    Also set API keys for models.

    We always default to True if a setting or env var is not present.
    """
    for model_id, model_config in LLM_MODELS.items():
      # Get enabled setting in model config
      model_config_enabled = model_config.get(KEY_ENABLED, "True")
      model_enabled = model_config_enabled.lower() == "true"
    
      # if there is no env flag variable for this model, or it is not set,
      # then env_flag_setting defaults to True
      env_flag_setting = True
      if "env_flag" in model_config:
        env_flag = model_config["env_flag"]
        env_flag_setting = get_environ_flag(env_flag)

      # Validate presence of provider config and determine whether the
      # provider is enabled. By default providers are enabled. If provider
      # config is not present model
      provider = model_config.get(KEY_PROVIDER, None)
      if provider is None:
        Logger.error(f"No provider for model {model_id}: disabling")
        model_config[KEY_ENABLED] = False
        continue
      provider_config = LLM_MODEL_PROVIDERS.get(provider, None)
      if provider_config is None:
        Logger.error(
            f"Provider config for model {model_id} not found: disabling")
        model_config[KEY_ENABLED] = False
        continue
      provider_enabled_setting = provider_config.get(KEY_ENABLED, "True")
      provider_enabled = provider_enabled_setting.lower() == "true"
    
      # Get api keys if present. If an api key serect is configured and
      # the key is missing, disable the model.
      api_key = get_api_key(model_id)
      api_check = True 
      if get_config_value(KEY_API_KEY):
        api_check = api_key is not None

      model_enabled = 
          api_check and \
          model_enabled and \
          provider_enabled and \
          env_flag_setting

      model_config[KEY_ENABLED] = model_enabled

      Logger.info(
          f"Setting model enabled flag for {model_id} to {model_enabled}")

  def is_model_enabled(self, model_id: str) -> bool:
    model_config = LLM_MODELS.get(model_id)
    return model_config(KEY_ENABLED)

  def get_model_config(self, model_id: str) -> dict: 
    model_config = LLM_MODELS.get(model_id, None)
    if model_config is None:
      raise ModelConfigMissingException(model_id)
    return model_config

  def get_config_value(model_id: str, key: str) -> Any:
    return get_model_config(model_id).get(key)

  def get_api_keys(self) -> dict:
    """ return a dict of model_id: api_key """
    api_keys = {}
    for model_id, _ in model_config.items():
      api_key = get_api_key(model_id: str)
      api_keys.update({model_id: api_key})
    return api_keys

  def get_api_key(self, model_id: str) -> str:
    """ Get api key for model.  Also set it into model config. """
    model_config = get_model_config(model_id)
    api_key = None
    if is_model_enabled(model_id):
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
              f"Unable to retrieve api key secret {api_key_id} for {model_id}")

    model_config["api_key_value"] = api_key
    return api_key

  def load_model_config(self):
    """ 
    Load model config dicts.  
    Refresh api keys and set enabled flags for all models.
    """
    read_model_config()
    set_model_config()
