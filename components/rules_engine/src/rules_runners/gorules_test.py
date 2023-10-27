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

"""
Unit test for gorules.py
"""
# disabling these rules, as they cause issues with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports
from models.rule import Rule
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from datetime import datetime
from models.ruleset import RuleSet
from gorules import GoRules

gorules = GoRules()

TEST_GORULES_RULES = {
  "contentType": "application/vnd.gorules.decision",
  "edges": [
    {
      "id": "0e0093d4-f765-434b-bc58-a3ed7a02263d",
      "type": "edge",
      "sourceId": "f146c369-59ec-4d9d-b946-cfc8630ef5c4",
      "targetId": "87e573c0-d089-423a-b910-c884e8060ddb"
    },
    {
      "id": "76a049ae-5475-42c7-bacc-61791fe0cdeb",
      "type": "edge",
      "sourceId": "87e573c0-d089-423a-b910-c884e8060ddb",
      "targetId": "629b6a98-b302-4cb6-ae7d-d3b839b4c3da"
    }
  ],
  "nodes": [
    {
      "id": "f146c369-59ec-4d9d-b946-cfc8630ef5c4",
      "name": "Request",
      "type": "inputNode",
      "position": {
        "x": 110,
        "y": 130
      }
    },
    {
      "id": "87e573c0-d089-423a-b910-c884e8060ddb",
      "name": "medicaid_decision",
      "type": "decisionTableNode",
      "content": {
        "hitPolicy": "first",
        "inputs": [
          {
            "id": "QL-eHAWyyq",
            "name": "Age",
            "type": "expression",
            "field": "profile.age"
          },
          {
            "id": "62J8ZCz0fv",
            "name": "No. of family members",
            "type": "expression",
            "field": "profile.family_members"
          },
          {
            "id": "uxZxdKWo2B",
            "name": "Household Income",
            "type": "expression",
            "field": "profile.household_income"
          },
          {
            "id": "kxF4XRPadP",
            "name": "Individual Income",
            "type": "expression",
            "field": "profile.individual_income"
          }
        ],
        "outputs": [
          {
            "id": "WJzDD6aMJo",
            "name": "Eligible",
            "type": "expression",
            "field": "eligible"
          }
        ],
        "rules": [
          {
            "_id": "HTxwVVhPQd",
            "QL-eHAWyyq": "<19",
            "62J8ZCz0fv": "",
            "uxZxdKWo2B": "",
            "kxF4XRPadP": "",
            "WJzDD6aMJo": "true"
          },
          {
            "_id": "RqC1pUvCO7",
            "QL-eHAWyyq": ">=65",
            "62J8ZCz0fv": "4",
            "uxZxdKWo2B": "<30000",
            "kxF4XRPadP": "",
            "WJzDD6aMJo": "true"
          },
          {
            "_id": "DZpZ9zJrcR",
            "QL-eHAWyyq": ">=65",
            "62J8ZCz0fv": "",
            "uxZxdKWo2B": "",
            "kxF4XRPadP": "",
            "WJzDD6aMJo": "true"
          },
          {
            "_id": "2LuKSbCK6v",
            "QL-eHAWyyq": "",
            "62J8ZCz0fv": "",
            "uxZxdKWo2B": "",
            "kxF4XRPadP": "",
            "WJzDD6aMJo": "false"
          }
        ]
      },
      "position": {
        "x": 420,
        "y": 130
      }
    },
    {
      "id": "629b6a98-b302-4cb6-ae7d-d3b839b4c3da",
      "name": "Response",
      "type": "outputNode",
      "position": {
        "x": 720,
        "y": 130
      }
    }
  ]
}

def test_load_rules_from_json(clean_firestore):
  gorules.load_rules_from_json(
    "ruleset-1",
    TEST_GORULES_RULES,
    create_new_ruleset=True)

  ruleset = RuleSet.find_by_doc_id("ruleset-1")
  assert ruleset is not None

  gorules_data = ruleset.runner_data["gorules"]
  assert gorules_data is not None

  rules = ruleset.rules
  assert len(rules) == 1

def test_evaluate(clean_firestore):
  gorules.load_rules_from_json(
    "ruleset-1",
    TEST_GORULES_RULES,
    create_new_ruleset=True)

  # Expect eligible==True when age < 19
  output = gorules.evaluate("ruleset-1", {
    "profile": {
      "age": 15
    }
  })
  assert output["result"]["eligible"] is True

  # Expect eligible==True when age >= 65
  output = gorules.evaluate("ruleset-1", {
    "profile": {
      "age": 70
    }
  })
  assert output["result"]["eligible"] is True

  # Expect eligible==False for the rest.
  output = gorules.evaluate("ruleset-1", {
    "profile": {
      "age": 20
    }
  })
  assert output["result"]["eligible"] is False
