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
Unit test for Rule.py
"""
# disabling these rules, as they cause issues with pytest fixtures
# pylint: disable=unused-import,unused-argument,redefined-outer-name
from models.ruleset import RuleSet
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from datetime import datetime


TEST_RULESET = {
  "name": "RuleSet name",
  "labels": ["foo", "bar"],
  "rules": [
    {
      "rule_id": "rule-1",
      "fields": {
        "field-1": "int",
        "field-2": "str",
      }
    },
    {
      "rule_id": "rule-2",
      "fields": {
        "field-1": "int",
        "field-2": "str",
      }
    },
  ]
}

def test_ruleset(clean_firestore):
  """Test for creating, loading and deleting of a new rule"""
  new_ruleset = RuleSet.from_dict(TEST_RULESET)
  new_ruleset.save()
  ruleset = RuleSet.find_by_id(new_ruleset.id)
  assert ruleset.name == TEST_RULESET["name"]
  assert ruleset.rules == TEST_RULESET["rules"]
  RuleSet.soft_delete_by_id(new_ruleset.id)
