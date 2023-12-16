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

from common.utils.logging_handler import Logger
from common.utils.request_handler import get_method, post_method
from langchain.tools import tool
from config import SERVICES, auth_client
from typing import List, Dict

Logger = Logger.get_logger(__file__)


def rules_engine_get_ruleset_fields(ruleset_name: str):
  """
  Call the rules engine to get the fields for a record
  """
  api_url_prefix = SERVICES["rules-engine"]["api_url_prefix"]
  api_url = f"{api_url_prefix}/ruleset/{ruleset_name}/fields"
  response = get_method(url=api_url,
                        auth_client=auth_client)
  fields = response.json().get("fields", {})
  return fields

@tool(infer_schema=True)
def gmail_tool(recipients: List, subject: str, message: str) -> str:
  """
  Send an email to a list of recipients
  """

  api_url_prefix = SERVICES["tools-service"]["api_url_prefix"]
  api_url = f"{api_url_prefix}/workspace/gmail"

  recipients = ",".join(recipients)
  data = {
    "recipient": recipients,
    "subject": subject,
    "message": message,
  }
  try:
    response = post_method(url=api_url,
                          request_body=data,
                          auth_client=auth_client)

    resp_data = response.json()
    result = resp_data["result"]
    recipient = resp_data["recipient"]
    output = f"[gmail_tool] Sending email to {recipient}. Result: {result}"
    Logger.info(output)

  except RuntimeError as e:
    output = f"[gmail_tool] Unable to send email: {e}"
    Logger.error(output)

  return output

@tool(infer_schema=True)
def docs_tool(recipients: List, content: str) -> Dict:
  """
  Compose or create a document using Google Docs
  """
  print(f"[docs_tool]: {recipients}")

  api_url_prefix = SERVICES["tools-service"]["api_url_prefix"]
  api_url = f"{api_url_prefix}/workspace/compose_email"

  # TODO: Add more template to support additional use cases.
  data = {
    "prompt":
      "Create an email to this applicant that is missing income verification "
      "asking them to email a pay stub from their employers",
    "email_template":
      "You are working for {state} agency. Create only the email message body "
      "\n\n Use text delimited by triple backticks "
      "to create the email body text:'''{email_body}'''",
    "variables": {
      "state": "NY",
    }
  }
  try:
    response = post_method(url=api_url,
                          request_body=data,
                          auth_client=auth_client)
    resp_data = response.json()
    subject = resp_data["subject"]
    output = resp_data["message"]
    Logger.info(f"[docs_tool] Composed an email with subject: {subject}")


    output = {
      "subject": resp_data["subject"],
      "message": resp_data["message"]
    }


  except RuntimeError as e:
    Logger.error(f"[gmail_tool] Unable to send email: {e}")
  return output

@tool(infer_schema=True)
def calendar_tool(date: str) -> str:
  """
  Create and update meetings using Google Calendar
  """
  print("[calendar_tool] calendar tool called:" + date)
  return ""

@tool(infer_schema=True)
def search_tool(query: str) -> str:
  """
  Perform an internet search.
  """
  print("[search_tool] search tool called: " + query)
  return ""

@tool(infer_schema=True)
def query_tool(query: str) -> Dict:
  """
  Perform a query and craft an answer using one of the available query engines.
  """


  # Use StructuredTool to let agent to pass output from previous tool..
  result = {
    "recipients": ["sumeetvij@google.com"]
  }

  return result

@tool(infer_schema=True)
def google_sheets_tool(
    name: str, columns: list, rows: list, user_email: str=None) -> dict:
  """
  Create a Google Sheet with the supplied data and return the sheet url and
  id
  """
  return create_google_sheet(name, columns, rows, user_email)

def create_google_sheet(name: str,
                        columns: list,
                        rows: list,
                        user_email: str=None) -> dict:
  """
  Call tools service to generate spreadsheet
  """
  Logger.info(
        f"[create_google_sheet] creating spreadsheet name: '{name}', "
        f" columns: {columns}"
        f" for user: {user_email}\n")
  api_url_prefix = SERVICES["tools-service"]["api_url_prefix"]
  api_url = f"{api_url_prefix}/workspace/sheets/create"
  output = {}

  # TODO: Add support with multiple emails.
  data = {
    "name": name,
    "columns": columns,
    "rows": rows,
    "share_emails": [user_email],
  }

  try:
    response = post_method(url=api_url,
                           request_body=data,
                           auth_client=auth_client)

    resp_data = response.json()
    Logger.info(
      f"[google_sheets_tool] response from google_sheets_service: \n{resp_data}"
      )
    status = resp_data.get("status")
    if status != "Success":
      raise RuntimeError("[google_sheets_tool] Failed to create google sheet: "
                         f"{resp_data['message']}")
    output = {
      "sheet_url": resp_data["sheet_url"],
      "sheet_id": resp_data["sheet_id"]
    }
  except RuntimeError as e:
    Logger.error(f"[google_sheets_tool] Unable to create Google Sheets: {e}")
  return output

@tool(infer_schema=True)
def database_tool(database_query: str) -> dict:
  """
    Accepts a natural language question and queries a database to get definite
    answer
  """
  Logger.info(
    f"[database_tool] executing query:{database_query}")
  api_url_prefix = SERVICES["tools-service"]["api_url_prefix"]
  api_url = f"{api_url_prefix}/workspace/database/query"
  output = {}
  data = {
    "query": database_query
  }
  try:
    response = post_method(url=api_url,
                           request_body=data,
                           auth_client=auth_client)

    resp_data = response.json()
    Logger.info(
      f"[database_tool] response from database_service: {response}"
      )
    result = resp_data["result"]
    Logger.info(
        f"[database_tool] query response:{resp_data}."
        f" Result: {result}")
    output = {
      "columns": resp_data["columns"],
      "rows": resp_data["rows"]
    }
  except RuntimeError as e:
    Logger.error(f"[database_tool] Unable to execute query: {e}")
  return output
