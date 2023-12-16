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
  Unit tests for LLM Service db agent
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports
import os
import pytest
import json
from unittest import mock
from config.utils import get_dataset_config
from services.agents.db_agent import run_db_agent

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"


FAKE_DB_AGENT_RESULT = "{\"columns\":[\"test\"],\"data\":[1,2,3]}"

FAKE_SPREADSHEET_OUTPUT = {"sheet_url": "test url"}

class FakeAgentExecutor():
  def run(self, prompt):
    return FAKE_DB_AGENT_RESULT

def test_run_db_agent():
  dataset_config = get_dataset_config()
  dataset = dataset_config.get("default")
  prompt = "how much data is too much?"
  with mock.patch("services.agents.db_agent.SQLDatabase"):
    with mock.patch("services.agents.db_agent.SQLStatementDBToolKit"):
      with mock.patch("services.agents.db_agent.create_sql_agent",
                      return_value=FakeAgentExecutor()):
        with mock.patch("services.agents.db_agent.create_google_sheet",
                        return_value=FAKE_SPREADSHEET_OUTPUT):
          output, _ = run_db_agent(prompt, dataset=dataset)
  assert output["data"] == json.loads(FAKE_DB_AGENT_RESULT)
  assert output["resources"]["Spreadsheet"] == "test url"
