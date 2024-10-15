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
from common.models.base_model_sql import SQLBaseModel
from common.utils.errors import ResourceNotFoundException
from playhouse.postgres_ext import ArrayField, JSONField
from peewee import (UUIDField, TextField, IntegerField,
                    BooleanField, DoesNotExist)


class User(SQLBaseModel):
  """User base Class"""
  user_id = UUIDField()
  first_name = TextField()
  last_name = TextField()
  email = TextField()
  user_type = TextField()
  user_type_ref = TextField(null=True)
  user_groups = ArrayField(null=True)
  status = TextField()
  is_registered = BooleanField(null=True)
  failed_login_attempts_count = IntegerField(null=True)
  access_api_docs = BooleanField(default=False)
  gaia_id = TextField(null=True)
  photo_url = TextField(null=True)
  inspace_user = JSONField(default={})
  is_deleted = BooleanField(default=False)

  def save(self, *args, **kwargs):
    """Overrides default method to save items with timestamp and validation."""

    from common.models.user import validate_name, check_status, check_user_type

    # Validation logic
    if not validate_name(self.first_name):
      raise ValueError("Invalid first name format")
    if not validate_name(self.last_name):
      raise ValueError("Invalid last name format")
    self.email = self.email.lower()  # Convert email to lowercase
    if not check_user_type(self.user_type):
      raise ValueError("Invalid user type")
    if not check_status(self.status):
      raise ValueError("Invalid status")

    return super().save(*args, **kwargs)

  @classmethod
  def find_by_user_id(cls, user_id, is_deleted=False):
    """Find the user using user_id
    Args:
        user_id (string): user_id of user
        is_deleted (boolean): is deleted
    Returns:
        user Object
    """
    try:
      return cls.get(
        cls.user_id == user_id,
        cls.is_deleted == is_deleted
      )
    except DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with user_id {user_id} not found"
      )

  @classmethod
  def find_by_uuid(cls, user_id, is_deleted=False):
    """Find the user using user_id
    Args:
        user_id (string): user_id of user
        is_deleted (boolean): is deleted
    Returns:
        user Object
    """
    try:
      return cls.get(
        cls.user_id == user_id,
        cls.is_deleted == is_deleted
      )
    except DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with user_id {user_id} not found"
      )

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
    try:
      return cls.get(cls.email == email)
    except DoesNotExist:
      return None

  @classmethod
  def find_by_status(cls, status):
    """Find the user using status
    Args:
        status (string): user's status
    Returns:
        List of User objects
    """
    list(
      cls.select().where(cls.status == status,
                         cls.is_deleted == False)
    )


  @classmethod
  def find_by_gaia_id(cls, gaia_id, is_deleted=False):
    """Find the user using gaia id
    Args:
        gaia_id (string): user's gaia_id
        is_deleted (boolean): is deleted
    Returns:
        User: User Object
    """
    try:
      return cls.get(
        cls.gaia_id == gaia_id,
        cls.is_deleted == is_deleted
      )
    except DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with gaia_id {gaia_id} not found"
      )

  @classmethod
  def find_by_user_type_ref(cls, user_type_ref, is_deleted=False):
    """Find the user using user_type_ref/learner_id
    Args:
      user_type_ref (string): User's user_type_ref
      is_deleted (boolean): is deleted
    Returns:
      User: User Object
    """
    try:
      return cls.get(
        cls.user_type_ref == user_type_ref,
        cls.is_deleted == is_deleted,
        )
    except DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with user_type_ref {user_type_ref} not found"
      )

  @classmethod
  def delete_by_uuid(cls, uuid):
    """Delete the user using user id
    Args:
        uuid (string): user's user_id
    Returns:
        None
    """
    try:
      user = cls.get(cls.user_id == uuid,
                     cls.is_deleted == False)
      user.is_deleted = True
      user.save()
    except DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with user_id {uuid} not found"
      )