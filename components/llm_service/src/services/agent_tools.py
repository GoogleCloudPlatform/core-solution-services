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

from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import get_method, post_method
from langchain.tools import tool
from config import RULES_ENGINE_BASE_URL, auth_client


MEDICAID_RECORD = "medicaid"

EXAMPLE_MEDICAID_RECORD = {
  "first_name": "str",
  "last_name": "str",
  "household_income": "int",
  "home_address": "str"
}


def rules_engine_get_record_fields(record_name: str):
  """
  Call the rules engine to get the fields for a record
  """
  record_url = f"{RULES_ENGINE_BASE_URL}/records/fields/{record_name}"
  record_fields = get_method(url=record_url,
                             auth_client=auth_client)
  return record_fields

@tool(infer_schema=False)
def medicaid_eligibility_requirements(record: str):
  """
  Get the required pieces of information and documents to apply for Medicaid
  benefits.
  """
  #record_fields = rules_engine_get_record_fields(MEDICAID_RECORD)

  record_fields = EXAMPLE_MEDICAID_RECORD

  return record_fields
