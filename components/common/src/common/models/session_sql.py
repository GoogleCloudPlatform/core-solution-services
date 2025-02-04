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
Session SQL Data Model
"""
import uuid
from peewee import TextField, BooleanField
from playhouse.postgres_ext import JSONField
from common.models.base_model_sql import SQLBaseModel
from common.utils.errors import ResourceNotFoundException


class Session(SQLBaseModel):
  """
  Data model class for User Session
  """
  session_id = TextField(primary_key=True, default=str(uuid.uuid4))
  user_id = TextField()
  parent_session_id = TextField(null=True)
  session_data = JSONField(null=True)
  session_desc = TextField(null=True)
  is_expired = BooleanField(default=False)

  class Meta:
    table_name = SQLBaseModel.DATABASE_PREFIX + "sessions"
    primary_key = False

  @property
  def id(self):
    return self.session_id

  @classmethod
  def find_by_uuid(cls, uuid):
    """
    Find a session by `session_id`.
    """
    try:
      return cls.get(cls.session_id == uuid)
    except cls.DoesNotExist:
      raise ResourceNotFoundException(
        f"Session with session_id {uuid} not found"
      )

  @classmethod
  def find_by_parent_session_id(cls, parent_session_id):
    """
    Find sessions by `parent_session_id`.
    """
    return list(
      cls.select().where(cls.parent_session_id == parent_session_id)
    )

  @classmethod
  def find_by_user_id(cls, user_id):
    """
    Find sessions by `user_id`.
    """
    return list(cls.select().where(cls.user_id == user_id))

  @classmethod
  def find_by_node_id(cls, node_id):
    """
    Find sessions by `node_id` inside `session_data`.
    """
    return list(
      cls.select().where(
        (cls.session_data['node_id'] == node_id)  # JSON field query
      )
    )
