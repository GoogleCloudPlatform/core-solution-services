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
from models.rule import Rule
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from datetime import datetime


TEST_RULE = {
  "name": "Rule name",
  "title": "Rule Title",
  "type": "Rule Type",
  "description": "Rule Description",
  "fields": ["Foo", "Bar"],
  "sql_query": "select employee_name from employee",
  "created_at": datetime(year=2022, month=10, day=14),
  "modified_at": datetime(year=2022, month=12, day=25)
}

def test_rule(clean_firestore):
  """Test for creating, loading and deleting of a new rule"""
  new_rule = Rule.from_dict(TEST_RULE)
  new_rule.save()
  rule = Rule.find_by_id(new_rule.id)
  assert rule.title == TEST_RULE["title"]
  assert rule.description == TEST_RULE["description"]
  Rule.soft_delete_by_id(new_rule.id)
