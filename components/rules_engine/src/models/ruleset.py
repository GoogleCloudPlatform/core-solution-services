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

"""Firebase Data model for RuleSet"""

from fireo.fields import IDField, TextField, ListField, Field
from fireo.queries.errors import ReferenceDocNotExist
from common.models.base_model import BaseModel

COLLECTION_NAME = BaseModel.DATABASE_PREFIX + "rulesets"

class RuleSet(BaseModel):
  """RuleSet ORM class"""

  class Meta:
    ignore_none_field = False
    collection_name = COLLECTION_NAME

  id = IDField()
  name = TextField()
  labels = ListField(str)
  rules = ListField()
  description = TextField()

  # To store any runner-specific ruleset data. E.g.
  # "runner_data": {
  #   "gorules": {
  #      ...
  #   }
  # }
  runner_data = Field()

  @classmethod
  def find_by_doc_id(cls, doc_id):
    try:
      ruleset = RuleSet.collection.get(f"{COLLECTION_NAME}/{doc_id}")
    except ReferenceDocNotExist:
      return None

    return ruleset
