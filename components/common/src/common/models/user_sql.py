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
User SQL Data Model
"""
# pylint: disable=unused-import
from peewee import (UUIDField,
                    DateTimeField,
                    TextField,
                    IntegerField,
                    BooleanField,
                    TimestampField)
from playhouse.postgres_ext import ArrayField, JSONField
from common.models.base_model_sql import SQLBaseModel
from common.models.user import validate_name, check_status, check_user_type


class User(SQLBaseModel):
  """User base Class"""
  user_id = UUIDField()
  first_name = TextField(validator=validate_name)
  last_name = TextField(validator=validate_name)
  email = TextField(to_lowercase=True)
  user_type = TextField(validator=check_user_type)
  user_type_ref = TextField(null=True)
  user_groups = ArrayField(null=True)
  status = TextField(validator=check_status)
  is_registered = BooleanField(null=True)
  failed_login_attempts_count = IntegerField(null=True)
  access_api_docs = BooleanField(default=False)
  gaia_id = TextField(null=True)
  photo_url = TextField(null=True)
  inspace_user = JSONField(default={})
  is_deleted = BooleanField(default=False)

  @classmethod
  def find_by_user_id(cls, user_id, is_deleted=False):
    """Find the user using user_id
    Args:
        user_id (string): user_id of user
        is_deleted (boolean): is deleted
    Returns:
        user Object
    """
    pass

  @classmethod
  def find_by_uuid(cls, user_id, is_deleted=False):
    """Find the user using user_id
    Args:
        user_id (string): user_id of user
        is_deleted (boolean): is deleted
    Returns:
        user Object
    """
    pass

  @classmethod
  def find_by_email(cls, email):
    """Find the user using email
    Args:
        email (string): user's email address
    Returns:
        User: User Object
    """
    if email:
      email = email.lower()
    pass

  @classmethod
  def find_by_status(cls, status):
    """Find the user using status
    Args:
        status (string): user's status
    Returns:
        List of User objects
    """
    pass

  @classmethod
  def find_by_gaia_id(cls, gaia_id, is_deleted=False):
    """Find the user using gaia id
    Args:
        gaia_id (string): user's gaia_id
        is_deleted (boolean): is deleted
    Returns:
        User: User Object
    """
    pass

  @classmethod
  def find_by_user_type_ref(cls, user_type_ref, is_deleted=False):
    """Find the user using user_type_ref/learner_id
    Args:
      user_type_ref (string): User's user_type_ref
      is_deleted (boolean): is deleted
    Returns:
      User: User Object
    """
    pass

  @classmethod
  def delete_by_uuid(cls, uuid):
    """Delete the user using user id
    Args:
        uuid (string): user's user_id
    Returns:
        None
    """
    pass
