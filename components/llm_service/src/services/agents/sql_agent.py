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

""" SQL Agent module """
import re
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from config import LANGCHAIN_LLM, PROJECT_ID, OPENAI_LLM_TYPE_GPT4
from services.agents.agent_prompts import SQL_QUERY_FORMAT_INSTRUCTIONS
from services.agents.utils import strip_punctuation_from_end

DATASET = "fqhc_medical_transactions"

def execute_sql_query(prompt:str,
                      llm_type:str=None,
                      db_creds=None) -> dict:
  """
  Execute a SQL database query based on a human prompt

  Args:
    prompt: human query
    llm_type: model id of llm to use to execute the query
    db_creds: path to service account file (optional)

  Return:
    a dict of "columns: column names, "data": row data
  """
  db_url = f"bigquery://{PROJECT_ID}/{DATASET}"
  if db_creds is not None:
    db_url = db_url + f"?credentials_path={db_creds}"

  db = SQLDatabase.from_uri(db_url)

  if llm_type is None:
    llm_type = OPENAI_LLM_TYPE_GPT4
  llm = LANGCHAIN_LLM[llm_type]

  toolkit = SQLDatabaseToolkit(db=db, llm=llm)

  agent_executor = create_sql_agent(
      llm=llm,
      toolkit=toolkit,
      verbose=True,
      top_k=300
  )
  clean_prompt = strip_punctuation_from_end(prompt)
  input_prompt = f"{clean_prompt}? {SQL_QUERY_FORMAT_INSTRUCTIONS}"

  return_val = agent_executor.run(input_prompt)

  return return_val

  