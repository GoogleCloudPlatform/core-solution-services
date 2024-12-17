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

# pylint: disable=unused-argument,unused-import,import-outside-toplevel
from typing import TypedDict, Optional
from common.utils.logging_handler import Logger
from common.utils.request_handler import get_method, post_method
from langchain.tools import tool as langchain_tool, StructuredTool
from config import SERVICES, auth_client
from typing import List, Dict
from vertexai.preview import extensions

Logger = Logger.get_logger(__file__)

# the agent tool decorator adds tools to this dict
# {
#    "tool_1 function name": langchain-wrapped-tool-function,
#    "tool_2 function name": langchain-wrapped-tool-function,
#    ...
# }
agent_tool_registry = {}

chat_tools = {"vertex_code_interpreter_tool"}

def agent_tool(*dec_args, **dec_kwargs):
  """ Extend langchain tool decorator to allow us to manage tools """

  def decorator(func):
    # call the langchain tool decorator on the tool function
    tool_func = langchain_tool(*dec_args, **dec_kwargs)(func)

    # add the tool to our registry
    agent_tool_registry.update({func.__name__: tool_func})

    return tool_func

  return decorator

# Tool definitions

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

def rules_engine_execute_ruleset(ruleset_name: str, rule_inputs: dict):
  """
  Call the rules engine to get the fields for a record
  """
  api_url_prefix = SERVICES["rules-engine"]["api_url_prefix"]
  api_url = f"{api_url_prefix}/ruleset/{ruleset_name}/evaluate"

  post_data = {

  }

  response = post_method(url=api_url,
                         request_body=post_data,
                         auth_client=auth_client)
  fields = response.json().get("fields", {})
  return fields

@agent_tool(infer_schema=True)
def ruleset_input_tool(ruleset_name: str) -> dict:
  """
  Get the list of required inputs to run a set of rules (a 'ruleset').
  The current available ruleset is a ruleset for medicaid eligibility.
  The output of this tool is a dict of input keys and corresponding data types.
  """
  return rules_engine_get_ruleset_fields(ruleset_name)


@agent_tool(infer_schema=True)
def ruleset_execute_tool(ruleset_name: str, rule_inputs: dict) -> dict:
  """
  Run a business rules engine to make determinations about medicaid
  eligibility. Takes a dict of constituent attributes as input (such as
  income level, demographic data etc - the full set of input keys is
  retrieved using the ruleset_input_tool).  Outputs an eligibility decision.
  """
  return rules_engine_execute_ruleset(ruleset_name, rule_inputs)


@agent_tool(infer_schema=True)
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
    Logger.info(f"resp_data: {resp_data}")
    result = resp_data.get("result")
    recipient = resp_data["recipient"]
    output = f"[gmail_tool] Sending email to {recipient}. Result: {result}"
    Logger.info(output)

  except RuntimeError as e:
    output = f"[gmail_tool] Unable to send email: {e}"
    Logger.error(output)

  return output

@agent_tool(infer_schema=True)
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

@agent_tool(infer_schema=True)
def calendar_tool(date: str) -> str:
  """
  Create and update meetings using Google Calendar
  """
  # TODO: implement this tool
  print("[calendar_tool] calendar tool called:" + date)
  return ""

@agent_tool(infer_schema=True)
def search_tool(query: str) -> str:
  """
  Perform an internet search.
  """
  # TODO: implement this tool
  print("[search_tool] search tool called: " + query)
  return ""

@agent_tool(infer_schema=True)
def query_tool(query: str) -> Dict:
  """
  Perform a query and craft an answer using one of the available query engines,
  with the name passed in as a argument.
  """
  # TODO: implement this tool
  result = {
    "recipients": ["jonchen@google.com"]
  }

  return result

@agent_tool(infer_schema=True)
def google_sheets_tool(
    name: str, columns: list, rows: list, user_email: str=None) -> dict:
  """
  Create a Google Sheet with the supplied data and return the sheet url and
  id
  """
  return create_google_sheet(name, columns, rows, user_email)

def create_google_sheet(name: str,
                        columns: List[str],
                        rows: List[List[str]],
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
  share_emails = []
  if user_email is not None:
    share_emails = [user_email]
  data = {
    "name": name,
    "columns": columns,
    "rows": rows,
    "share_emails": share_emails
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

@agent_tool(infer_schema=True)
async def database_tool(database_query_prompt: str) -> dict:
  """
    Accepts a natural language question and queries a database to get an
    answer in the form of data.
  """
  tool_description = """
  Accepts a natural language question and queries a relational database using
  SQL to get an answer, in the form of rows of data."
  """
  langchain_database_tool = StructuredTool.from_function(
      name="database_tool",
      description=tool_description,
      coroutine=execute_db_query
  )

  # run the tool
  response = await langchain_database_tool.arun(database_query_prompt)

  return response


async def execute_db_query(database_query_prompt: str) -> dict:
  Logger.info(
    f"[database_tool] executing query:{database_query_prompt}")
  output = {}
  try:
    from services.agents.db_agent import run_db_agent
    resp_data = await run_db_agent(database_query_prompt)

    output = resp_data
  except RuntimeError as e:
    Logger.error(f"[database_tool] Unable to execute query: {e}")
  return output

def vertex_code_interpreter_tool(query: str) -> dict:
  """
    Answers questions requiring generating code. Get the results of a natural 
    language query by generating and executing a 
    code snippet. Can generate graph output as images.
    query: The natural language query to get the results for.
  """
  extension_code_interpreter = extensions.Extension.from_hub("code_interpreter")
  response = extension_code_interpreter.execute(
    operation_id = "generate_and_execute",
    operation_params = {"query": query},
  )
  return response

class FileInResponse(TypedDict):
  name: str
  contents: str # the base64 encoding of that file's contents
def run_chat_tools(prompt: str) -> tuple[str, Optional[list[FileInResponse]]]:
  """Takes a prompt and returns the result of running tools against it
  The results are returned as a tuple consisting of a first elements
  with the text response and a second element containing a list of files
  with the filename in a 'name' field and the base64 encoded contents of the
  file in the 'contents' field"""
  # for now assume code interpreter is used as it is the only chat tool
  response_files = None
  tool_response = vertex_code_interpreter_tool(prompt)
  if tool_error := tool_response["execution_error"]:
    response = tool_error
  else:
    response = (f"Code generated\n\n```{tool_response['generated_code']}```"
                "Execution result from the code: "
                f"```{tool_response['execution_result']}```")
    response_files = tool_response["output_files"]
  return response, response_files
