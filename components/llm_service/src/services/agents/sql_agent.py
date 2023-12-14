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
import json
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from common.utils.http_exceptions import InternalServerError
from config import (LANGCHAIN_LLM, PROJECT_ID,
                    OPENAI_LLM_TYPE_GPT4, AGENT_DATASET_CONFIG_PATH)
from services.agents.agent_prompts import SQL_QUERY_FORMAT_INSTRUCTIONS
from services.agents.utils import strip_punctuation_from_end

DATASETS = None

def load_datasets(agent_dataset_config_path: str):
  """ load agent dataset config """
  global DATASETS
  try:
    dataset_config = {}
    with open(agent_dataset_config_path, "r", encoding="utf-8") as file:
      dataset_config = json.load(file)
    DATASETS = dataset_config
  except Exception as e:
    raise InternalServerError(
        f" Error loading agent dataset config: {e}") from e

def get_dataset_config() -> dict:
  if DATASETS is None:
    load_datasets(AGENT_DATASET_CONFIG_PATH)
  return DATASETS

def run_db_agent(prompt: str, llm_type: str) -> dict:
  """
  Run the DB agent and return the resulting data. 

  Return:
    a dict of "columns: column names, "data": row data
  """
  dataset, db_type = map_prompt_to_dataset(prompt, llm_type)
  if db_type == "SQL":
    results = execute_sql_query(prompt, dataset, llm_type)
  else:
    raise InternalServerError(f"Unsupported agent db type {db_type}")
  return results

def map_prompt_to_dataset(prompt: str, llm_type: str) -> str:
  """
  Determine the dataset based on the prompt
  """
  datasets = get_dataset_config()

  # TODO: use LLM to map datatype
  dataset = "fqhc_medical_transactions"

  db_type = datasets.get(dataset).get("type")
  return dataset, db_type

def execute_sql_query(prompt: str,
                      dataset: str,
                      llm_type: str=None,
                      ) -> dict:
  """
  Execute a SQL database query based on a human prompt.
  Currently hardcoded to target bigquery.

  Args:
    prompt: human query
    dataset: dataset id (from agent dataset config)
    llm_type: model id of llm to use to execute the query

  Return:
    a dict of "columns: column names, "data": row data
  """
  db_url = f"bigquery://{PROJECT_ID}/{dataset}"

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

  