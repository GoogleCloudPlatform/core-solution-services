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

"""Runner implementation for GoRules engine. (gorules.io)"""

import zen
import json
from rules_runners.base_runner import BaseRulesRunner
from models.ruleset import RuleSet

class GoRules(BaseRulesRunner):
  """GoRules Rules Runner implementation.

  Args:
      BaseRulesRunner: RulesRunner base class with required functions.
  """

  def __init__(self):
    self.engine = zen.ZenEngine()

  def load_rules_from_json(self,
                           ruleset_id: str,
                           data: dict,
                           create_new_ruleset: bool=True):
    """Load and parse rulse from a JSON file.

    Args:
        ruleset_id (str): RuleSet doc_id
        data (dict): JSON data
        create_new_ruleset (bool, optional): Whether to create a
            new RuleSet if it doesn't exist.
    """
    ruleset = RuleSet.find_by_doc_id(ruleset_id)
    if create_new_ruleset and not ruleset:
      ruleset = RuleSet()
      ruleset.id = ruleset_id
      ruleset.name = ruleset_id
      ruleset.description = ""
      ruleset.rules = []

    # TODO: Delete all existing rules if any.

    assert "nodes" in data, "'nodes' is not in the data."
    decision_table_nodes = filter(
        lambda x: x["type"] == "decisionTableNode", data["nodes"])

    # Build index for all input nodes. When using GoRules editor,
    # it creates a hashed ID for each nodes (input, output, etc).
    all_fields = {}
    for node in decision_table_nodes:
      for input_item in node["content"]["inputs"]:
        all_fields[input_item["field"]] = input_item

    # Create one single rule to contain all GoRules rules.
    # TODO: Break rules into multiple Rule data model.
    ruleset.rules = [{
      "fields": all_fields,
    }]

    # Save raw json into runner_data
    ruleset.runner_data = {}
    ruleset.runner_data["gorules"] = {
      "rules_raw_json": data,
      "fields": all_fields,
    }

    ruleset.save()


  def evaluate(self,
               ruleset_id: str,
               content: dict) -> dict:
    """Evaluate a dict content against a ruleset.

    Args:
        ruleset_id (str): RuleSet doc_id
        content (dict): Content in dict format.

    Returns:
        dict: Evaluation result.
    """
    ruleset = RuleSet.find_by_doc_id(ruleset_id)
    assert ruleset, f"Ruleset {ruleset_id} not found."

    rules_data = ruleset.runner_data["gorules"]["rules_raw_json"]
    rules_json = json.dumps(rules_data)
    decision = self.engine.create_decision(rules_json)
    result = decision.evaluate(content)
    return result
