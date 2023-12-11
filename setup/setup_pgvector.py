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

import argparse
import sqlalchemy
from sqlalchemy.orm import Session

def get_input(prompt):
  input_value = None
  while not input_value:
    input_value = input(prompt)
  return input_value

def init_database(connection_params, database):
  connection_string = f"postgresql+psycopg2://{connection_params}/postgres"
  engine = sqlalchemy.create_engine(connection_string)
  connection = engine.connect()

  try:
    with Session(connection) as session:
      statement = sqlalchemy.text(f"CREATE DATABASE {database}")
      session.execute(statement)
      session.commit()
  except Exception as e:
    raise Exception(f"Failed to create database: {e}") from e

  try:
    with Session(connection) as session:
      statement = sqlalchemy.text("CREATE EXTENSION IF NOT EXISTS vector")
      session.execute(statement)
      session.commit()
  except Exception as e:
    raise Exception(f"Failed to create vector extension: {e}") from e


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  help_str = "postgres connection string: [<user>:<password>@<host>:<port>]"
  parser.add_argument("connection", type=str, help=help_str)
  help_str = "postgres database name"
  parser.add_argument("database", type=str, help=help_str)
  args = parser.parse_args()
  
  if not args.connection:
    connection_string = get_input("Enter postgres connection params: <user>:<password>@<host>:<port>")
  else:
    connection_string = args.connection
    print(f"Connection string: {connection_string}")
  assert connection_string, "connection_string is empty."
  
  init_database(connection_string, database_name)