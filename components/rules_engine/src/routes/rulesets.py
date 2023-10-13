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

from fastapi import APIRouter, HTTPException
from models.rule import Rule
from schemas.rule import RuleSchema
import datetime

# disabling for linting to pass
# pylint: disable = broad-except

router = APIRouter(prefix="/ruleset", tags=["ruleset"])

SUCCESS_RESPONSE = {"status": "Success"}

MOCK_RULESET = {
  "id": "ruleset-1",
  "labels": ["eligibility"],
  "name": "Financial eligibility",
  "rules": [
    {
      "description": "Income must be below the Federal Poverty Level (FPL). The FPL for 2023 is $14,580 for an individual and $30,000 for a family of four",
      "fields": {
        "Individual Income": int,
        "Family Income": int,
      },
      "sql_query": "",
    },
    {
      "description": "Citizenship or immigration status: Must be a U.S. citizen, a qualified non-citizen, or a qualified immigrant",
      "fields": {
        "Citizenship or immigration status": str
      },
      "sql_query": "",
    },
    {
      "description": "Medicaid beneficiaries must be residents of the state in which they are applying",
      "fields": {
        "Resident state": str
      },
      "sql_query": "",
    },
    {
      "description": "Medicaid is available to all children under age 19, regardless of their family's income; Medicaid is available to people who are 65 years old or older and meet certain income and asset requirements.",
      "fields": {
        "Age": int
      },
      "sql_query": "",
    },
    {
      "description": "Disability status: People with disabilities may be eligible for Medicaid if they meet certain criteria. The criteria vary from state to state, but they typically involve having a physical or mental impairment that limits major life activities.",
      "fields": {
        "Disability status": str
      },
      "sql_query": "",
    },
    {
      "description": "Pregnancy",
      "fields": {
        "Pregnancy status": str
      },
      "sql_query": "",
    },
    {
      "description": "Nursing home residency: People who live in nursing homes may be eligible for Medicaid if they meet certain income and asset requirements",
      "fields": {
        "Nursing home residency": str
      },
      "sql_query": "",
    },
    {
      "description": "HCBS eligibility: People who receive HCBS may be eligible for Medicaid if they meet certain income and asset requirements. HCBS are waiver services that are provided outside of a nursing home or other institution.",
      "fields": {
        "HCBS status": str
      },
      "sql_query": "",
    },
  ],
}



@router.get("/{id}")
async def get(id: str):
  """Get a Ruleset

  Args:
    id (str): unique id of the ruleset

  Raises:
    HTTPException: 404 Not Found if ruleset doesn't exist for the given id
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    ruleset: a ruleset object that contains a list of rules.
  """

  return MOCK_RULESET


@router.get("/{id}/fields")
async def get_fields(id: str):

  fields = {}
  for rule in MOCK_RULESET["rules"]:
    fields.update(rule.get("fields", {}))

  return {
    "fields": fields
  }
