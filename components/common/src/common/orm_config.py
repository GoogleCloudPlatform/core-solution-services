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
Config module to setup common ORM environment
"""
# pylint: disable=broad-exception-caught
from common.utils.config import get_env_setting
from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret

Logger = Logger.get_logger(__file__)

# postgres settings
# TODO: create secrets for this
PG_DBNAME = get_env_setting("PG_DBNAME", "genie_db")
PG_HOST = get_env_setting("PG_HOST", "127.0.0.1")
PG_PORT = get_env_setting("PG_PORT", "5432")
PG_USER = get_env_setting("PG_USER", "postgres")
PG_PASSWD = get_env_setting("PG_PASSWD", None)

if not PG_PASSWD:
  # load secrets
  try:
    PG_PASSWD = get_secret("postgres-user-passwd")
  except Exception as e:
    Logger.warning("Can't access postgres user password secret")
    PG_PASSWD = None

Logger.info(f"PG_HOST = [{PG_HOST}]")
Logger.info(f"PG_DBNAME = [{PG_DBNAME}]")
Logger.info(f"PG_USER = [{PG_USER}]")
Logger.info(f"PG_PASSWD = [{PG_PASSWD}]")


# ORM config.  See common.models.__init__.py
SQL_ORM = "sql_orm"
FIRESTORE_ORM = "firestore_orm"
ORM_MODE = get_env_setting("ORM_MODE", SQL_ORM)
Logger.info(f"ORM_MODE = [{ORM_MODE}]")
