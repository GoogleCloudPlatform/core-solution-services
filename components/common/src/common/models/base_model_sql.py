# Copyright 2024 Google LLC
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
SQL BaseModel to be inherited by all other objects for SQL ORM
"""
import datetime
from typing import List, Tuple
from common.orm_config import PG_HOST, PG_DBNAME, PG_USER, PG_PASSWD
from common.utils.errors import ResourceNotFoundException
from peewee import Model, DoesNotExist, DateTimeField, TextField
from playhouse.postgres_ext import PostgresqlExtDatabase

# pylint: disable=unused-argument

# instantiate connection to postgres db
db = PostgresqlExtDatabase(
  PG_DBNAME, host=PG_HOST, password=PG_PASSWD, user=PG_USER
)

class SQLBaseModel(Model):
  """
  BaseModel for SQL-based data models
  """
  created_time = DateTimeField(default=datetime.datetime.utcnow)
  last_modified_time = DateTimeField(default=datetime.datetime.utcnow)
  deleted_at_timestamp = DateTimeField(null=True)
  deleted_by = TextField(default="")
  archived_at_timestamp = DateTimeField(null=True)
  archived_by = TextField(default="")
  created_by = TextField(default="")
  last_modified_by = TextField(default="")

  class Meta:
    database = db
    legacy_table_names = False

  @property
  def collection(self):
    """
    Provides access to the model's collection-like interface.

    This property mimics Fireo's `collection` attribute, allowing you to
    access methods like `filter()` without changing dependent code.
    """

    # Create a simple object with a `filter` method
    class CollectionWrapper:
      @classmethod
      def filter(cls, *args, **kwargs):
        # Delegate to the model's filter method
        return self.filter(*args, **kwargs)

    return CollectionWrapper

  @classmethod
  def filter(cls, *args, **kwargs):
    """
    Filter objects in the database based on the given conditions.
    This method provides a way to filter objects similar to
    Fireo's `collection.filter()`.
    It uses Peewee's `where()` method to apply the filter conditions.
    Args:
        *args: Positional arguments for the `where()` method.
        **kwargs: Keyword arguments for the `where()` method.
    Returns:
        A query object that can be further refined or used to fetch objects.
    """
    return cls.select().where(*args, **kwargs)

  @classmethod
  def find_by_id(cls, doc_id):
    """Looks up in the Database and returns an object of this type by id
       (not key)
        Args:
            doc_id (string): the document id
        Returns:
            [any]: an instance of object returned by the database, type is
            the subclassed Model,
            None if object not found
        """
    try:
      obj = cls.get(cls.id == doc_id)
    except DoesNotExist:
      obj = None
    return obj

  def save(self,
           input_datetime=None,
           transaction=None,
           batch=None,
           merge=None,
           no_return=False):
    """
    Overrides default method to save items with timestamp
    Args:
      input_datetime (_type_, optional): _description_. Defaults to None.
      transaction (_type_, optional): _description_. Defaults to None.
      batch (_type_, optional): _description_. Defaults to None.
      merge (_type_, optional): _description_. Defaults to None.
      no_return (bool, optional): _description_. Defaults to False.
    Returns:
      _type_: _description_
    """
    if input_datetime:
      date_timestamp = input_datetime
    else:
      date_timestamp = datetime.datetime.utcnow()
    self.created_time = date_timestamp
    self.last_modified_time = date_timestamp
    return super().save()

  def update(self,
             input_datetime=None,
             key=None,
             transaction=None,
             batch=None):
    """overrides default method to update items with timestamp
    Args:
      input_datetime (_type_, optional): _description_. Defaults to None.
      key (_type_, optional): _description_. Defaults to None.
      transaction (_type_, optional): _description_. Defaults to None.
      batch (_type_, optional): _description_. Defaults to None.
    Returns:
      _type_: _description_
    """
    if input_datetime:
      date_timestamp = input_datetime
    else:
      date_timestamp = datetime.datetime.utcnow()
    self.last_modified_time = date_timestamp
    return super().save()

  @classmethod
  def delete_by_id(cls, doc_id):
    """Deletes from the Database the object of this type by id (not key)

        Args:
            doc_id (string): the document id without collection_name
            (i.e. not the key)
        Returns:
            None
        """
    return cls.delete().where(cls.id == doc_id).execute()

  @classmethod
  def soft_delete_by_id(cls, object_id, by_user=None):
    """Soft delete an object by id
      Args:
          object_id (str): unique id
          by_user
      Raises:
          ResourceNotFoundException: If the object does not exist
      """
    try:
      obj = cls.find_by_id(object_id)
      obj.deleted_at_timestamp = datetime.datetime.utcnow()
      obj.deleted_by = by_user
      obj.save()
    except DoesNotExist as ex:
      raise ResourceNotFoundException(
        f"{cls.__name__} with id {object_id} is not found") from ex

  @classmethod
  def fetch_all(cls, skip=0, limit=1000, order_by="-created_time"):
    """ fetch all documents
    Args:
        skip (int, optional): _description_. Defaults to 0.
        limit (int, optional): _description_. Defaults to 1000.
        order_by (str, optional): _description_. Defaults to "-created_time".
    Returns:
        list: list of objects
    """
    order_by_field = getattr(cls, order_by[1:])
    if order_by.startswith("-"):
      order_by_field = order_by_field.desc()
    objects = cls.select().order_by(order_by_field).offset(skip).limit(limit)
    return list(objects)

  @classmethod
  def get_fields(cls, reformat_datetime=False, remove_meta=False):
    """
    Overrides default method to fix data type for datetime fields.
    remove_meta=True will remove extra meta data fields (useful for testing)
    """
    fields = {}
    for field_name in cls._meta.sorted_field_names:
      field_value = getattr(cls, field_name)
      if isinstance(field_value, datetime.datetime) and reformat_datetime:
        field_value = str(field_value)
      fields[field_name] = field_value
    if remove_meta:
      fields = cls.remove_field_meta(fields)
    return fields

  @classmethod
  def remove_field_meta(cls, fields: dict) -> dict:
    """Remove meta keys from the fields dictionary."""
    del fields["created_time"]
    del fields["created_by"]
    del fields["archived_at_timestamp"]
    del fields["archived_by"]
    del fields["deleted_at_timestamp"]
    del fields["deleted_by"]
    del fields["last_modified_time"]
    del fields["last_modified_by"]
    return fields

  @classmethod
  def validate(cls) -> Tuple[bool, List[str]]:
    """
    Validate a model in this class.

    Returns:
      True,[] or False, list of error messages
    """
    errors = []
    # Placeholder for validation logic.
    # Add custom validation rules here for model fields.
    return len(errors) == 0, errors
