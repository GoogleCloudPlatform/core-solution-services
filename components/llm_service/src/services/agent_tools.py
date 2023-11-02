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

MEDICAID_RULESET = "medicaid_ny"

EXAMPLE_MEDICAID_FIELDS_1 = {
  "Individual Income": "int",
  "Family Income": "int",
  "Citizenship or immigration status": "str",
  "Resident state": "str",
  "Age": "int",
  "Disability status": "str",
  "Pregnancy status": "str",
  "Nursing home residency": "str",
}

EXAMPLE_MEDICAID_FIELDS_2 = {
  "first_name": "str",
  "last_name": "str",
  "household_income": "int",
  "home_address": "str"
}

EXAMPLE_CRM_RECORD = {
  "first_name": "Jane",
  "last_name": "Doe",
  "case_history": [
    {
      "11-01-2023 11:54:00 GMT": "Submitted an application for Medicaid",
      "11-02-2023 10:00:00 GMT":
        "Agency sent email asking for more information about household income",
      "11-04-2023 14:20:00 GMT":
        "Recieved income verfication in the form of a pay stub",
    }
  ]
}

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
def medicaid_eligibility_requirements(record: str) -> str:
  """
  Get the required pieces of information and documents to apply for Medicaid
  benefits.
  """
  fields = rules_engine_get_ruleset_fields(MEDICAID_RULESET)
  #fields = EXAMPLE_MEDICAID_FIELDS_2

  return fields

@tool(infer_schema=False)
def medicaid_eligibility_check(record: str) -> str:
  """
  Check whether an applicant qualifies for Medicaid.
  """
  fields = rules_engine_get_ruleset_fields(MEDICAID_RULESET)
  #fields = EXAMPLE_MEDICAID_FIELDS_2

  return fields

@tool(infer_schema=False)
def medicaid_crm_update(name:str):
#def medicaid_crm_update(first_name:str,
#                        last_name:str,
#                        ssn:str = None,
#                        dob:str = None) -> str:
  """
  Update a CRM record for medicaid enrollees
  """
  return "CRM record updated."

@tool(infer_schema=False)
#def medicaid_crm_retrieve(first_name:str,
#                          last_name:str,
#                          ssn:str = None,
#                          dob:str = None) -> str:
def medicaid_crm_retrieve(name:str):
  """
  Retrieve a CRM record for medicaid enrollees
  """
  crm_record = EXAMPLE_CRM_RECORD

  return crm_record

@tool(infer_schema=False)
def medicaid_policy_retrieve(query: str) -> str:
  """
  Perform a query related to medicaid policies
  """

  return ""

@tool(infer_schema=False)
def gmail_tool(email_text: str) -> str:
  """
  Send an email using Gmail
  """
  return ""

@tool(infer_schema=False)
def docs_tool(content: str) -> str:
  """
  Compose a document using Google Docs
  """

  return ""

@tool(infer_schema=False)
def calendar_tool(date: str) -> str:
  """
  Create and update meetings using Google Calendar
  """

  return ""
