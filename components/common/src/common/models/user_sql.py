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
import uuid
from peewee import (
  TextField,
  IntegerField,
  BooleanField
)
from playhouse.postgres_ext import ArrayField, JSONField
from common.models.base_model_sql import SQLBaseModel
from common.utils.errors import ResourceNotFoundException

# Define custom user types as a list below.
USER_TYPES = [
  "user", "learner", "faculty", "assessor", "admin", "coach",
  "instructor", "lxe", "curriculum_designer", "robot"
]


def validate_name(name):
  """Validator method to validate name"""
  import regex
  if regex.fullmatch(r"[\D\p{L}\p{N}\s]+$", name):
    return True
  else:
    return False, "Invalid name format"


def check_user_type(field_val):
  """Validator method for user type field"""
  if field_val.lower() in USER_TYPES:
    return True
  return False, f"User Type must be one of {', '.join(USER_TYPES)}"


def check_status(field_val):
  """Validator method for status field"""
  status = ["active", "inactive"]
  if field_val.lower() in status:
    return True
  return False, f"Status must be one of {', '.join(status)}"


class User(SQLBaseModel):
  """
  User SQL Model
  """
  user_id = TextField(primary_key=True, default=str(uuid.uuid4))
  first_name = TextField()
  last_name = TextField()
  email = TextField()
  user_type = TextField()
  user_type_ref = TextField(null=True)
  user_groups = ArrayField(TextField, null=True)
  status = TextField()
  is_registered = BooleanField(default=False)
  failed_login_attempts_count = IntegerField(default=0)
  access_api_docs = BooleanField(default=False)
  gaia_id = TextField(null=True)
  photo_url = TextField(null=True)
  inspace_user = JSONField(default=dict)
  is_deleted = BooleanField(default=False)

  class Meta:
    table_name = SQLBaseModel.DATABASE_PREFIX + "users"
    primary_key = False

  @property
  def id(self):
    return self.user_id

  def save(self, *args, **kwargs):
    """
    Save with validation logic
    """
    if not validate_name(self.first_name):
      raise ValueError("Invalid first name format")
    if not validate_name(self.last_name):
      raise ValueError("Invalid last name format")
    self.email = self.email.lower()
    if not check_user_type(self.user_type):
      raise ValueError("Invalid user type")
    if not check_status(self.status):
      raise ValueError("Invalid status")
    super().save(*args, **kwargs)

  @classmethod
  def find_by_user_id(cls, user_id, is_deleted=False):
    """
    Find the user using user_id
    """
    try:
      return cls.get(
        (cls.user_id == user_id) & (cls.is_deleted == is_deleted)
      )
    except cls.DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with user_id {user_id} not found"
      )

  @classmethod
  def find_by_email(cls, email):
    """
    Find the user using email
    """
    try:
      email = email.lower()
      return cls.get(cls.email == email)
    except cls.DoesNotExist:
      return None

  @classmethod
  def find_by_status(cls, status):
    """
    Find users by status
    """
    return list(
      cls.select().where(
        (cls.status == status) & (cls.is_deleted == False)  # noqa
      )
    )

  @classmethod
  def find_by_gaia_id(cls, gaia_id, is_deleted=False):
    """
    Find the user using gaia_id
    """
    try:
      return cls.get(
        (cls.gaia_id == gaia_id) & (cls.is_deleted == is_deleted)
      )
    except cls.DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with gaia_id {gaia_id} not found"
      )

  @classmethod
  def find_by_user_type_ref(cls, user_type_ref, is_deleted=False):
    """
    Find the user using user_type_ref
    """
    try:
      return cls.get(
        (cls.user_type_ref == user_type_ref)
        & (cls.is_deleted == is_deleted)
      )
    except cls.DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with user_type_ref {user_type_ref} not found"
      )

  @classmethod
  def delete_by_uuid(cls, uuid):
    """
    Soft delete the user using user_id
    """
    try:
      user = cls.get(cls.user_id == uuid, cls.is_deleted == False)  # noqa
      user.is_deleted = True
      user.save()
    except cls.DoesNotExist:
      raise ResourceNotFoundException(
        f"{cls.__name__} with user_id {uuid} not found"
      )
