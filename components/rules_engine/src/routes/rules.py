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

""" Rule endpoints """

from fastapi import APIRouter, HTTPException
from models.rule import Rule
from schemas.rule import RuleSchema
import datetime

router = APIRouter(prefix="/rule", tags=["rule"])

SUCCESS_RESPONSE = {"status": "Success"}


@router.get("/{rule_id}", response_model=RuleSchema)
async def get(rule_id: str):
  """Get a Rule

  Args:
    rule_id (str): unique id of the rule

  Raises:
    HTTPException: 404 Not Found if rule doesn't exist for the given rule id
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [rule]: rule object for the provided rule id
  """
  rule = Rule.find_by_doc_id(rule_id)

  if rule is None:
    raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found.")
  return rule


@router.post("")
async def post(data: RuleSchema):
  """Create a Rule

  Args:
    data (Rule): Required body of the rule

  Raises:
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [JSON]: rule ID of the rule if the rule is successfully created
  """
  rule_id = data.id
  existing_rule = Rule.find_by_doc_id(rule_id)

  if existing_rule:
    raise HTTPException(status_code=409,
                        detail=f"Rule {rule_id} already exists.")

  new_rule = Rule()
  new_rule = new_rule.from_dict({**data.dict()})
  new_rule.created_at = datetime.datetime.utcnow()
  new_rule.modified_at = datetime.datetime.utcnow()
  new_rule.save()

  return SUCCESS_RESPONSE


@router.put("")
async def put(data: RuleSchema):
  """Update a Rule

  Args:
    data (Rule): Required body of the rule

  Raises:
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [JSON]: {'status': 'Succeed'} if the rule is updated
  """
  rule_id = data.id
  rule = Rule.find_by_doc_id(rule_id)

  if rule:
    rule = rule.from_dict({**data.dict()})
    rule.modified_at = datetime.datetime.utcnow()
    rule.save()

  else:
    raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found.")

  return SUCCESS_RESPONSE


@router.delete("/{rule_id}")
async def delete(rule_id: str):
  """Delete a Rule

  Args:
    rule_id (str): unique id of the rule

  Raises:
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [JSON]: {'status': 'Succeed'} if the rule is deleted
  """

  rule = Rule.find_by_doc_id(rule_id)
  if rule is None:
    raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found.")

  Rule.collection.delete(rule.key)

  return SUCCESS_RESPONSE
