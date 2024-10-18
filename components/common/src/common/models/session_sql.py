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

"""Session SQL Data Model"""

from fireo.fields import (TextField, MapField, BooleanField)
from common.models.base_model_sql import SQLBaseModel
from common.utils.errors import ResourceNotFoundException


class Session(SQLBaseModel):
  """Data model class for Learner Profile"""
  # schema for object
  session_id = TextField(required=True)
  user_id = TextField(required=True)
  parent_session_id = TextField(default=None)
  session_data = MapField(default=None)
  is_expired = BooleanField(default=False)

  @classmethod
  def find_by_uuid(cls, uuid):
    session = cls.get("session_id", "==", uuid)
    if session is None:
      raise ResourceNotFoundException(
          f"Session with session_id {uuid} not found")
    return session

  @classmethod
  def find_by_parent_session_id(cls, parent_session_id):
    sessions = cls.get("parent_session_id", "==", parent_session_id)
    return sessions

  @classmethod
  def find_by_user_id(cls, user_id):
    """Find the session using user id
    Args:
        user_id (string): session user id
    Returns:
        Session: Session Object
    """
    sessions = cls.get("user_id", "==", user_id)
    return sessions

  @classmethod
  def find_by_node_id(cls, node_id):
    """Find the session using node id
    Args:
        node_id (string): session node id
    Returns:
        Session: Session Object
    """
    sessions = cls.get("session_data.node_id", "==", node_id)
    return sessions
