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
Base class for Node items
"""
import sys
from common.models import BaseModel, NodeItem
from fireo.fields import TextField, NumberField, MapField

class UserEvent(NodeItem):
  """UserEvent model class"""

  # should be a reference field if we have session data model
  session_ref = TextField(required=False, default="")
  is_correct = NumberField(required=False)
  learning_item_id = TextField(required=True)
  activity_type = TextField(required=True)
  raw_response = MapField(required=False, default={})
  user_id = TextField(required=True)
  feedback = MapField(required=False, default={})
  learning_unit = TextField(required=True)
  course_id = TextField(required=True, default="")
  flow_type = TextField(required=True, default="Let AITutor Guide Me")
  context = TextField(required=True, default="")
  hint = MapField(required=False, default={})

  class Meta:
    collection_name = BaseModel.DATABASE_PREFIX + "user_events"
    ignore_none_field = False

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    # leaf node
    self.children_nodes = None
