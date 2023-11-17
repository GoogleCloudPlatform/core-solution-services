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

from langchain.agents import Tool, AgentExecutor, BaseMultiActionAgent, AgentOutputParser
from langchain.tools.gmail.utils import build_resource_service, get_gmail_credentials
from langchain.agents.agent_toolkits import GmailToolkit
from langchain.agents import initialize_agent, AgentType
from langchain.agents.chat.base import ChatAgent
from langchain.prompts import StringPromptTemplate, ChatPromptTemplate, PromptTemplate
from langchain.llms import OpenAI, VertexAI
from langchain.chat_models import ChatVertexAI, ChatOpenAI
from langchain.utilities import SerpAPIWrapper
from langchain.chains import LLMChain
from typing import List, Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException

from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import get_method, post_method
from langchain.tools import tool
from config import SERVICES, auth_client

Logger = Logger.get_logger(__file__)


# TODO: This is a workaround without using StructuredToolChat.
# For inter-tool communication.
tools_context = {}


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
def gmail_tool(email_text: str) -> str:
  """
  Send an email to a list of recipients
  """
  print(f"[gmail_tool]: {email_text}")

  # api_url_prefix = SERVICES["tools-service"]["api_url_prefix"]
  api_url_prefix = "https://gcp-mira-demo.cloudpssolutions.com/tools-service/api/v1"
  api_url = f"{api_url_prefix}/workspace/gmail"

  # TODO: Replace the usage of context with StructuredToolChat agent.
  recipients = ",".join(tools_context["query_tool"]["recipients"])
  subject = tools_context["docs_tool"]["subject"]
  message = tools_context["docs_tool"]["message"]

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
def docs_tool(content: str) -> str:
  """
  Compose or create a document using Google Docs
  """
  print(f"[docs_tool]: {content}")

  # api_url_prefix = SERVICES["tools-service"]["api_url_prefix"]
  api_url_prefix = "https://gcp-mira-demo.cloudpssolutions.com/tools-service/" \
                   "api/v1"
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

    # Adding to tools_context
    tools_context["docs_tool"] = {
      "subject": resp_data["subject"],
      "message": resp_data["message"],
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
def query_tool(query: str) -> str:
  """
  Perform a query and craft an answer using one of the available query engines.
  """
  print("[query_tool] query tool called: " + query)

  # TODO: Use StructuredToolChat to let agent to pass output from previous tool.
  # Adding context for other tool to use as a workaround.
  result = {
    "recipients": ["jonchen@google.com"]
  }
  tools_context["query_tool"] = result

  return result
