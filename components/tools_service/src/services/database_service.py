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
# pylint: disable=unused-argument

from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)

def execute_query(query: str) -> dict:
  """
    Execute a new database query.
    Args:
        query: String
    Returns:
        {rows, columns}
  """
  # TODO implement generic SQL query
  pass
