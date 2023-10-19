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

MEDICAID_RULESET = "medicaid"

EXAMPLE_MEDICAID_FIELDS = {
  "Individual Income": "int",
  "Family Income": "int",
  "Citizenship or immigration status": "str",
  "Resident state": "str",
  "Age": "int",
  "Disability status": "str",
  "Pregnancy status": "str",
  "Nursing home residency": "str",
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
def medicaid_eligibility_requirements(record: str):
  """
  Get the required pieces of information and documents to apply for Medicaid
  benefits.
  """
  # fields = rules_engine_get_ruleset_fields(MEDICAID_RULESET)
  fields = EXAMPLE_MEDICAID_FIELDS

  return fields
