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
# Data model for Rule. See https://octabyte.io/FireO/ for details.


import os

from fireo.models import Model
from fireo.fields import IDField, TextField, BooleanField, DateTime, ListField
from fireo.queries.errors import ReferenceDocNotExist
from datetime import datetime
from common.models.base_model import BaseModel

# GCP project_id from system's environment variable.
PROJECT_ID = os.environ.get("PROJECT_ID", "")

# Database prefix for integration and e2e test purpose.
DATABASE_PREFIX = os.getenv("DATABASE_PREFIX", "")


# Firebase data model in "rules" collection.
class Rule(BaseModel):
  """Rule ORM class"""

  class Meta:
    ignore_none_field = False
    collection_name = DATABASE_PREFIX + "rules"

  id = IDField()
  title = TextField()
  description = TextField()
  type = TextField()
  fields = ListField()
  created_at = DateTime()
  modified_at = DateTime()

  @classmethod
  def find_by_doc_id(cls, id):
    try:
      rule = Rule.collection.get(f"rules/{id}")
    except ReferenceDocNotExist:
      return None

    return rule