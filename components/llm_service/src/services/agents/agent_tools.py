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

""" Agent tools """

# pylint: disable=unused-argument,unused-import

from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import get_method, post_method
from langchain.tools import tool
from config import RULES_ENGINE_BASE_URL, auth_client


def rules_engine_get_ruleset_fields(ruleset_name: str):
  """
  Call the rules engine to get the fields for a record
  """
  api_url = f"{RULES_ENGINE_BASE_URL}/ruleset/{ruleset_name}/fields"
  response = get_method(url=api_url,
                        auth_client=auth_client)
  fields = response.json().get("fields", {})
  return fields

@tool(infer_schema=False)
def gmail_tool(email_text: str) -> str:
  """
  Send an email using Gmail
  """
  print("!!! gmail tool called: "+email_text)
  return ""

@tool(infer_schema=False)
def docs_tool(content: str) -> str:
  """
  Create a document using Google Docs
  """
  print("!!! docs tool called:"+content)
  return ""

@tool(infer_schema=False)
def calendar_tool(date: str) -> str:
  """
  Create and update meetings using Google Calendar
  """
  print("!!! calendar tool called:"+date)
  return ""

@tool(infer_schema=False)
def search_tool(query: str) -> str:
  """
  Perform an internet search.
  """
  print("!!! search tool called:"+query)
  return ""


@tool(infer_schema=False)
def query_tool(query: str) -> str:
  """
  Perform a query and craft an answer using one of the available query engines.
  """
  print("!!! query tool called:"+query)
  return ""
