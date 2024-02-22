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
Vector Store Config
"""
# pylint: disable=broad-exception-caught

from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
from common.utils.config import get_env_setting
from google.cloud import secretmanager

Logger = Logger.get_logger(__file__)

# vector store types
VECTOR_STORE_MATCHING_ENGINE = "matching_engine"
VECTOR_STORE_LANGCHAIN_PGVECTOR = "langchain_pgvector"
PG_VECTOR_DEFAULT_DBNAME = "pgvector"
LOCAL_HOST = "127.0.0.1"

VECTOR_STORES = [
  VECTOR_STORE_MATCHING_ENGINE,
  VECTOR_STORE_LANGCHAIN_PGVECTOR
]

# default vector store used for query engines
DEFAULT_VECTOR_STORE = get_env_setting("DEFAULT_VECTOR_STORE",
                                       VECTOR_STORE_MATCHING_ENGINE)
Logger.info(f"Default vector store = [{DEFAULT_VECTOR_STORE}]")

# postgres
# TODO: create secrets for this
PG_HOST = get_env_setting("PG_HOST", LOCAL_HOST)
PG_DBNAME = get_env_setting("PG_DBNAME", PG_VECTOR_DEFAULT_DBNAME)
PG_PORT = "5432"
PG_USER = "postgres"
PG_PASSWD = None
Logger.info(f"PG_HOST = [{PG_HOST}]")
Logger.info(f"PG_DBNAME = [{PG_DBNAME}]")

# load secrets
secrets = secretmanager.SecretManagerServiceClient()
try:
  PG_PASSWD = get_secret("postgres-user-passwd")
except Exception as e:
  Logger.warning("Can't access postgres user password secret")
  PG_PASSWD = None

# test postgres connection
if PG_PASSWD and PG_HOST:
  import sqlalchemy
  from langchain.vectorstores.pgvector import PGVector as LangchainPGVector
  try:
    connection_string = LangchainPGVector.connection_string_from_db_params(
        driver="psycopg2",
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DBNAME,
        user=PG_USER,
        password=PG_PASSWD
    )
    engine = sqlalchemy.create_engine(connection_string)
    conn = engine.connect()
    Logger.info(f"Connected successfully to pgvector instance at {PG_HOST}")
  except Exception as e:
    Logger.error(f"Cannot connect to pgvector instance at {PG_HOST}: {str(e)}")
