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
  LLM Service utils file
"""
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught,import-outside-toplevel


import json
from typing import List
from config.config import get_model_config


def get_config_list(config_str: str) -> List[str]:
  """ get a list of items from config """
  if config_str is None:
    return []
  config_list = config_str.split(",")
  config_list = [s.strip() for s in config_list]
  return config_list

def load_config_json(file_path: str):
  """ load a config JSON file """
  try:
    with open(file_path, "r", encoding="utf-8") as file:
      return json.load(file)
  except Exception as e:
    raise RuntimeError(
        f" Error loading config file {file_path}: {e}") from e

# Helper methods for config retrieval
def get_provider_models(provider_id):
  return get_model_config().get_provider_models(provider_id)

def get_provider_embedding_types(provider_id):
  return get_model_config().get_provider_embedding_types(provider_id)

def get_provider_value(provider_id, key, model_id=None, default=None):
  return get_model_config().get_provider_value(
      provider_id, key, model_id, default)

def get_provider_config(provider_id):
  return get_model_config().get_provider_config(provider_id)

def get_provider_model_config(provider_id):
  return get_model_config().get_provider_model_config(provider_id)
