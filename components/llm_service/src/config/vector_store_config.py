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

import os
from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
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
DEFAULT_VECTOR_STORE = os.getenv("DEFAULT_VECTOR_STORE",
                                  VECTOR_STORE_LANGCHAIN_PGVECTOR)
Logger.info(f"Default vector store = [{DEFAULT_VECTOR_STORE}]")

# postgres
# TODO: create secrets for this
PG_HOST = os.getenv("PG_HOST", LOCAL_HOST)
PG_DBNAME = os.getenv("PG_DBNAME", PG_VECTOR_DEFAULT_DBNAME)
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
