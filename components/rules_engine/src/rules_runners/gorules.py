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

from rules_runners.base_runner import BaseRulesRunner
from models.rule import Rule
from models.ruleset import RuleSet

class GoRules(BaseRulesRunner):
  """GoRules Rules Runner implementation.

  Args:
      BaseRulesRunner: RulesRunner base class with required functions.
  """

  def __init__(self):
    pass

  def load_rules_from_json(self, data: dict, ruleset_id: str):
    # TODO: Implement logic to load a JSON into a specific RuleSet and
    # Rules data models.
    pass

  def evaluate(self) -> bool:
    # TODO: Implement the rules execution with this rules engine.
    return False
