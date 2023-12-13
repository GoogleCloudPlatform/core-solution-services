# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tools and utils for database"""


from sqlalchemy import *
from sqlalchemy.engine import create_engine
from sqlalchemy.schema import *
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.agents import AgentExecutor



from config import PROJECT_ID, DATASET, LANGCHAIN_LLM,OPENAI_LLM_TYPE_GPT4
from utils.google_credential import get_bigquery_credential
from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)

def execute_query(
    query: str) -> dict:
  """
    Execute a new database query.
    Args:
        query: String
    Returns:
        {rows, columns}
  """

  service_account_file = get_bigquery_credential()
  dataset = DATASET

  sqlalchemy_url = f'bigquery://{PROJECT_ID}/{dataset}?credentials_path={service_account_file}'
  db = SQLDatabase.from_uri(sqlalchemy_url)
  # TODO: Add options to use VertexAI and other models.
  llm = LANGCHAIN_LLM[OPENAI_LLM_TYPE_GPT4]
  toolkit = SQLDatabaseToolkit(db=db, llm=llm)
  agent_executor = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    top_k=200
  )
  returnVal = agent_executor.run(query)


  return {
    "columns": returnVal["columns"],
    "rows":  returnVal["data"]
  }
