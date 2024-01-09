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


import inspect
import json
from config.config import (AGENT_DATASET_CONFIG_PATH,
                           AGENT_CONFIG_PATH,
                           get_model_config)

# global config for datasets and agents
DATASETS = None
AGENTS = None

def get_dataset_config() -> dict:
  global DATASETS

  if DATASETS is None:
    DATASETS = load_config_json(AGENT_DATASET_CONFIG_PATH)
  return DATASETS

def load_agents(agent_config_path: str):
  global AGENTS
  try:
    agent_config = load_config_json(agent_config_path)
    agent_config = agent_config.get("Agents")

    # add agent class and capabilities
    from services.agents import agents
    agent_classes = {
      k:klass for (k, klass) in inspect.getmembers(agents)
      if isinstance(klass, type)
    }
    for values in agent_config.values():
      agent_class = agent_classes.get(values["agent_class"])
      values["agent_class"] = agent_class
      values["capabilities"] = [c.value for c in agent_class.capabilities()]

    AGENTS = agent_config
  except Exception as e:
    raise RuntimeError(f" Error loading agent config: {e}") from e

def get_agent_config() -> dict:
  if AGENTS is None:
    load_agents(AGENT_CONFIG_PATH)
  return AGENTS


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
