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
Unit test for section.py
"""
# disabling these rules, as they cause issues with pytest fixtures
# pylint: disable=unused-import,unused-argument,redefined-outer-name
import os
import pytest
from config.model_config import ModelConfig
from common.testing.firestore_emulator import clean_firestore, firestore_emulator

TEST_MODEL_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "models.json")

def test_model_config_load():
  """test for creating and loading model config"""
  model_config = ModelConfig(TEST_MODEL_CONFIG_PATH)
  model_config.load_model_config()
