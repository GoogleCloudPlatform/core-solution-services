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

"""Session Data Model"""

from fireo.fields import (TextField, MapField, BooleanField)
from common.models.base_model import BaseModel
from common.utils.errors import ResourceNotFoundException


class Session(BaseModel):
  """Data model class for User Session"""
  # schema for object
  session_id = TextField(required=True)
  user_id = TextField(required=True)
  parent_session_id = TextField(default=None)
  session_data = MapField(default=None)
  is_expired = BooleanField(default=False)

  class Meta:
    collection_name = BaseModel.DATABASE_PREFIX + "v3_sessions"
    ignore_none_field = False

  @classmethod
  def find_by_uuid(cls, uuid):
    session = Session.collection.filter("session_id", "==", uuid).get()
    if session is None:
      raise ResourceNotFoundException(
          f"Session with session_id {uuid} not found")
    return session

  @classmethod
  def find_by_parent_session_id(cls, parent_session_id):
    sessions = Session.collection.filter("parent_session_id", "==",
                                         parent_session_id).fetch()
    return sessions

  @classmethod
  def find_by_user_id(cls, user_id):
    """Find the session using user id
    Args:
        user_id (string): session user id
    Returns:
        Session: Session Object
    """
    sessions = Session.collection.filter(
      "user_id", "==", user_id).fetch()
    return sessions

  @classmethod
  def find_by_node_id(cls, node_id):
    """Find the session using node id
    Args:
        node_id (string): session node id
    Returns:
        Session: Session Object
    """
    sessions = Session.collection.filter(
      "session_data.node_id", "==", node_id).fetch()
    return sessions
