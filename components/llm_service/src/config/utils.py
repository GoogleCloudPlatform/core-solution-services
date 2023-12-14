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

import json
from config import AGENT_DATASET_CONFIG_PATH


def get_dataset_config() -> dict:
  return load_config_json(AGENT_DATASET_CONFIG_PATH)


def load_config_json(file_path: str):
  """ load a config JSON file """
  try:
    with open(file_path, "r", encoding="utf-8") as file:
      return json.load(file)
  except Exception as e:
    raise RuntimeError(
        f" Error loading config file {file_path}: {e}") from e
