# Copyright 2024 Google LLC
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
  LLM Service agent config
"""
# pylint: disable=unspecified-encoding,line-too-long,broad-exception-caught

import inspect
import json
import os
from typing import List
from common.models import Agent

# agent config
AGENT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "agent_config.json")

AGENT_DATASET_CONFIG_PATH = \
    os.path.join(os.path.dirname(__file__), "agent_datasets.json")

# global config for datasets and agents
DATASETS = None
AGENTS = None

def get_dataset_config() -> dict:
  global DATASETS

  if DATASETS is None:
    DATASETS = load_config_json(AGENT_DATASET_CONFIG_PATH)
  return DATASETS

def load_agent_config(agent_config_path: str):
  """
  Load agent config from a filepath
  """
  try:
    agent_config = load_config_json(agent_config_path)
    set_agent_config(agent_config)
  except Exception as e:
    raise RuntimeError(f" Error loading agent config: {e}") from e

def set_agent_config(agent_config: dict):
  """
  Validate agent config and update agent models
  """
  global AGENTS

  agent_config = agent_config.get("Agents", None)
  if agent_config is None:
    raise RuntimeError("Missing agent config")

  # add agent class and capabilities
  from services.agents import agents
  agent_classes = {
    k:klass for (k, klass) in inspect.getmembers(agents)
    if isinstance(klass, type)
  }
  # update agent config dict for each agent
  for values in agent_config.values():
    agent_class_val = values["agent_class"]
    agent_class = agent_classes.get(agent_class_val)
    if agent_class is None:
      raise RuntimeError(f"Cannot find agent class {agent_class_val}")
    values["agent_class"] = agent_class
    values["capabilities"] = [c.value for c in agent_class.capabilities()]

  # validate config according to Agent model
  # for each agent, save or update model according to config
  for agent_name, ac_dict in agent_config.items():
    agent_model = Agent.find_by_name(agent_name)
    if not agent_model:
      agent_model = Agent()
    agent_model.name = agent_name
    agent_model.tools = get_config_list(ac_dict.get("tools"))
    agent_model.llm_type = ac_dict.get("llm_type")
    agent_model.capabilities = ac_dict["capabilities"]
    agent_model.agent_type = ac_dict.get("agent_type")

    # validate agent model in case config is invalid
    valid, validation_errors = agent_model.validate()
    if not valid:
      raise RuntimeError(
          f"Invalid Agent config for {agent_name}: {validation_errors}")

    # update agent model
    agent_model.save(merge=True)

  AGENTS = agent_config

def get_agent_config() -> dict:
  if AGENTS is None:
    load_agent_config(AGENT_CONFIG_PATH)
  return AGENTS
