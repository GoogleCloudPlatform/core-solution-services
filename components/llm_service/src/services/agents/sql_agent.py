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
from common import config 
from config import (VERTEX_LLM_TYPE_BISON_CHAT,
                    VERTEX_LLM_TYPE_BISON_TEXT,
                    VERTEX_AI_MODEL_GARDEN_LLAMA2_CHAT,
                    OPENAI_LLM_TYPE_GPT3_5,
                    OPENAI_LLM_TYPE_GPT4,
                    LLM_BACKEND_ROBOT_USERNAME,
                    LLM_BACKEND_ROBOT_PASSWORD,
                    LANGCHAIN_LLM,
                    REGION)
from common.utils.token_handler import UserCredentials
config.TOOLS_SERVICE_BASE_URL = f"https://{PROJECT_ID}.cloudpssolutions.com/tools-service/api/v1"
config.auth_client = UserCredentials(LLM_BACKEND_ROBOT_USERNAME,
                              LLM_BACKEND_ROBOT_PASSWORD,
                              f"https:/{PROJECT_ID}.cloudpssolutions.com")

from google.cloud import bigquery
from langchain.agents import create_sql_agent
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.sql_database import SQLDatabase
from langchain.llms.openai import OpenAI
from langchain.chat_models import ChatVertexAI
from langchain_experimental.sql import SQLDatabaseChain

service_account_file = "./data/gcp-mira-develop-gce-service-account.json"

DATASET = "fqhc_medical_transactions"


def execute_sql_query(prompt:str, llm_type:str=None) -> dict:
  """
  Execute a SQL database query based on a human prompt

  Args:
    prompt: human query
    llm_type: model id of llm to use to execute the query

  Return:
    a dict of "columns: column names, "data": row data
  """
  sqlalchemy_url = f"bigquery://{PROJECT_ID}/{DATASET}" \
                    "?credentials_path={service_account_file}"

  db = SQLDatabase.from_uri(sqlalchemy_url)
  
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
  
  return_val = agent_executor.run(prompt)
  