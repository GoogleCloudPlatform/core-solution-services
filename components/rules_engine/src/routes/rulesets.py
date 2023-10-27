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

""" Ruleset endpoints """

from fastapi import APIRouter
from schemas.ruleset import RulesetFieldsSchema, RulesetRulesImportSchema
from schemas.evaluation_result import EvaluationResultSchema
from rules_runners.gorules import GoRules
from models.ruleset import RuleSet

router = APIRouter(prefix="/ruleset", tags=["ruleset"])

RULES_RUNNERS = {
  "gorules": GoRules()
}

SUCCESS_RESPONSE = {"status": "Success"}


@router.get("/{ruleset_id}")
async def get(ruleset_id: str):
  """Get a Ruleset

  Args:
    ruleset_id (str): unique id of the RuleSet

  Raises:
    HTTPException: 404 Not Found if RuleSet doesn't exist for the given id
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    ruleset: a ruleset object that contains a list of rules.
  """

  print(ruleset_id)
  return RuleSet.find_by_doc_id(ruleset_id)


@router.get("/{ruleset_id}/fields", response_model=RulesetFieldsSchema)
async def get_fields(ruleset_id: str):
  """Get all fields in a RuleSet

  Args:
    ruleset_id (str): unique id of the ruleset

  Raises:
    HTTPException: 404 Not Found if ruleset doesn't exist for the given id
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    ruleset: an array of field names in a RuleSet
  """

  fields = {}
  ruleset = RuleSet.find_by_doc_id(ruleset_id)

  for rule in ruleset.rules:
    for field_detail in rule.get("fields", {}).values():
      fields[field_detail["name"]] = field_detail["type"]

  return {
    "fields": fields
  }


@router.post("/{ruleset_id}/import_rules")
async def import_rules(
  data: RulesetRulesImportSchema,
  ruleset_id: str,
  rules_runner: str="gorules"):
  """Import and parse JSON into a RuleSet and corresponding Rules.

  Args:
    ruleset_id (str): unique id of the ruleset
    data (str): A JSON string data.

  Raises:
    HTTPException: 404 Not Found if ruleset doesn't exist for the given id
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    ruleset_id: The ID of a newly imported RuleSet.
  """

  runner = RULES_RUNNERS.get(rules_runner)

  if not runner:
    return {
      "rules_runner": rules_runner,
      "status": "Error",
      "message": f"Rules_runner '{rules_runner}' is not defined."
    }

  # Pass request to the corresponding Rules Runner. E.g. GoRules.
  runner.load_rules_from_json(ruleset_id, data.rules_data)

  return {
    "ruleset_id": ruleset_id,
    "status": "Success",
  }


# TODO: Replace record (dict) with actual Record data model.
@router.post("/{ruleset_id}/evaluate",
             response_model=EvaluationResultSchema)
async def evaluate(
    ruleset_id: str, record: dict, rules_runner: str="gorules"):
  """Execute a ruleset against a particular record.

  Args:
    ruleset_id (str): unique id of the ruleset
    record (Record): a record object.

  Raises:
    HTTPException: 404 Not Found if ruleset doesn't exist for the given id
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    ruleset: an array of field names in a RuleSet
  """

  runner = RULES_RUNNERS.get(rules_runner)

  if not runner:
    return {
      "rules_runner": rules_runner,
      "status": "Error",
      "message": f"Rules_runner '{rules_runner}' is not defined."
    }

  output = runner.evaluate(ruleset_id, record)

  return {
    "rules_runner": rules_runner,
    "status": "Success",
    "result": output.get("result", None),
  }
