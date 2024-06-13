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
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports,wrong-import-position
import os
import pytest
from unittest import mock
from config import get_model_config, PROVIDER_LANGCHAIN
from testing.test_config import TEST_OPENAI_CONFIG

from services.agents.db_agent import run_db_agent

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"


FAKE_SQL_QUERY_RESULT = {
  "columns": ["test"],
  "rows": [[1],[2],[3]]
}

FAKE_SQL_QUERY_RESPONSE = [
  {"test": 1}, {"test": 2}, {"test": 3}
]

FAKE_SQL_STATEMENT = "SELECT test FROM testdb"

FAKE_SPREADSHEET_OUTPUT = {"sheet_url": "test url"}

FAKE_DATABASE_CONFIG = {
  "dataset-1": {
    "description": "Some description about this dataset",
    "type": "SQL"
  }
}

class FakeAgentExecutor():
  async def arun(self, prompt):
    return FAKE_SQL_STATEMENT

class FakeQuerySQLDataBaseTool():
  def run(self, statement):
    return str(FAKE_SQL_QUERY_RESULT["rows"])

@pytest.mark.asyncio
@mock.patch("services.agents.db_agent.SQLDatabase")
@mock.patch("services.agents.db_agent.SQLStatementDBToolKit")
@mock.patch("services.agents.db_agent.create_sql_agent")
@mock.patch("services.agents.db_agent.QuerySQLDataBaseTool")
@mock.patch("services.agents.db_agent.create_google_sheet")
async def test_run_db_agent(mock_create_google_sheet,
                            mock_query_sql_database_tool,
                            mock_create_sql_agent,
                            mock_sql_statement_db_toolkit,
                            mock_sql_database):
  """Test run_db_agent"""
  get_model_config().llm_model_providers = {
    PROVIDER_LANGCHAIN: TEST_OPENAI_CONFIG
  }
  get_model_config().llm_models = TEST_OPENAI_CONFIG

  mock_create_google_sheet.return_value = FAKE_SPREADSHEET_OUTPUT
  mock_query_sql_database_tool.return_value = FakeQuerySQLDataBaseTool()
  mock_create_sql_agent.return_value = FakeAgentExecutor()
  mock_sql_statement_db_toolkit.return_value = {}
  mock_sql_database.return_value = {}

  dataset_config = FAKE_DATABASE_CONFIG
  dataset = dataset_config.get("default")
  prompt = "how much data is too much?"
  output, _ = await run_db_agent(prompt, dataset=dataset)

  assert output["db_result"] == FAKE_SQL_QUERY_RESPONSE
  assert output["resources"]["Spreadsheet"] == "test url"
