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
import uuid
from typing import List, Tuple
import common.config
from common.config import PG_HOST, PG_DBNAME, PG_USER, PG_PASSWD
from common.utils.errors import ResourceNotFoundException
from peewee import Model, DoesNotExist, DateTimeField, TextField
from playhouse.postgres_ext import PostgresqlExtDatabase

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
  DATABASE_PREFIX = common.config.DATABASE_PREFIX

  class Meta:
    database = db
    legacy_table_names = False
    abstract = True

  @property
  def id(self):
    """
    Returns the value of the primary key field.
    """
    return getattr(self, self._meta.primary_key.name)

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
  def from_dict(cls, data):
    instance = cls()
    for key, value in data.items():
      if key in cls._meta.fields:
        setattr(instance, key, value)
    return instance

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
    query = cls.select()
    if args:
      query = query.where(*args)
    if kwargs:
      # Convert kwargs to Peewee-compatible expressions
      for field, value in kwargs.items():
        query = query.where(getattr(cls, field) == value)
    return query

  @classmethod
  def find_by_id(cls, pk):
    """
    Find an object by primary key.
    """
    try:
      return cls.get_by_id(pk)
    except DoesNotExist:
      raise ResourceNotFoundException(f"{cls.__name__} with id {pk} not found")

  def to_dict(self, reformat_datetime=False, remove_meta=False) -> dict:
    """
    Convert the model instance to a dictionary.
    Args:
        reformat_datetime (bool): Convert datetime fields to string.
        remove_meta (bool): Remove meta fields like timestamps and audit fields.
    Returns:
        dict: Dictionary representation of the instance.
    """
    data = {}
    for field_name in self._meta.sorted_field_names:
      field_value = getattr(self, field_name, None)
      if isinstance(field_value, datetime.datetime) and reformat_datetime:
        field_value = field_value.isoformat()
      data[field_name] = field_value

    # Include primary key under 'id' if it is not explicitly named
    if "id" not in data:
      data["id"] = getattr(self, self._meta.primary_key.name)

    if remove_meta:
      data = self.remove_field_meta(data)
    return data

  def save(self, force_insert=False, *args, **kwargs):
    """
    Save the instance to the database.
    Automatically handles inserting new records or updating existing ones.
    """
    try:
      # Check if the primary key is null and generate one if needed
      primary_key_field = self._meta.primary_key.name
      primary_key_value = getattr(self, primary_key_field, None)
      if not primary_key_value or primary_key_value.strip() == "":
        new_pk = str(uuid.uuid4())
        print(f"Generating new primary key: {new_pk}")
        setattr(self, primary_key_field, new_pk)

      # Determine if this is a new record based on the primary key existence
      is_new_instance = not self.__class__.select().where(
        self.__class__._meta.primary_key == # noqa
          getattr(self, primary_key_field)).exists()

      # Update timestamps
      date_timestamp = datetime.datetime.utcnow()
      if is_new_instance or force_insert:
        self.created_time = date_timestamp
      self.last_modified_time = date_timestamp

      # Insert or update based on `created_time`
      if is_new_instance or force_insert:
        print("Inserting new record.")
        return super().save(force_insert=True, *args, **kwargs)
      else:
        print("Updating existing record.")
        return super().save(force_insert=False, *args, **kwargs)
    except Exception as e:
      raise

  def update_instance(self, input_datetime=None, **update_fields):
    """
    Updates instance fields and refreshes the `last_modified_time`.
    Args:
        input_datetime (datetime): Timestamp for modification.
        update_fields (dict): Fields to update with values.
    """
    date_timestamp = input_datetime or datetime.datetime.utcnow()
    update_fields['last_modified_time'] = date_timestamp
    query = type(self).update(**update_fields).where(type(self).id == self.id)
    return query.execute()

  @classmethod
  def soft_delete_by_id(cls, object_id, by_user=""):
    """
    Soft delete an object by setting `deleted_at_timestamp` and `deleted_by`.
    """
    try:
      obj = cls.get(cls.id == object_id, cls.deleted_at_timestamp.is_null(True))
      obj.deleted_at_timestamp = datetime.datetime.utcnow()
      obj.deleted_by = by_user
      obj.save()
    except DoesNotExist:
      raise ResourceNotFoundException(f"{cls.__name__} with id {object_id} not found")

  @classmethod
  def archive_by_id(cls, object_id, by_user=""):
    """
    Archive an object by setting `archived_at_timestamp` and `archived_by`.
    """
    try:
      obj = cls.get(cls.id == object_id, cls.deleted_at_timestamp.is_null(True))
      obj.archived_at_timestamp = datetime.datetime.utcnow()
      obj.archived_by = by_user
      obj.save()
    except DoesNotExist:
      raise ResourceNotFoundException(f"{cls.__name__} with id {object_id} not found")

  @classmethod
  def fetch_all(cls, skip=0, limit=1000, order_by="-created_time"):
    """
    Fetch all objects with optional skip, limit, and ordering.
    """
    order_field = getattr(cls, order_by.lstrip("-"), cls.created_time)
    if order_by.startswith("-"):
      order_field = order_field.desc()
    query = cls.select().where(cls.deleted_at_timestamp.is_null(True)).order_by(order_field).offset(skip).limit(limit)
    return list(query)

  def get_fields(self, reformat_datetime=False, remove_meta=False):
    """
    Overrides default method to fix data type for datetime fields.
    remove_meta=True will remove extra meta data fields (useful for testing)
    """
    fields = {}
    for field_name in self._meta.sorted_field_names:
      field_value = getattr(self, field_name, None)
      if isinstance(field_value, datetime.datetime) and reformat_datetime:
        field_value = field_value.isoformat()
      fields[field_name] = field_value

    # Include primary key under 'id' if it is not explicitly named
    if "id" not in fields:
      fields["id"] = getattr(self, self._meta.primary_key.name)

    if remove_meta:
      fields = self.remove_field_meta(fields)

    return fields

  @classmethod
  def remove_field_meta(cls, fields: dict) -> dict:
    """
    Remove meta fields from the dictionary representation.
    Args:
        fields (dict): Dictionary to clean.
    Returns:
        dict: Cleaned dictionary without meta fields.
    """
    meta_fields = [
      "created_time", "last_modified_time", "deleted_at_timestamp",
      "deleted_by", "archived_at_timestamp", "archived_by",
      "created_by", "last_modified_by"
    ]
    return {key: value for key, value in fields.items() if key not in meta_fields}

  @classmethod
  def fetch_all_documents(cls, limit=1000):
    """
    Fetch all documents (records) in batches.
    """
    query = cls.select().where(cls.deleted_at_timestamp.is_null(True)).limit(limit)
    all_docs = []
    while True:
      docs = list(query)
      if not docs:
        break
      all_docs.extend(docs)
      if len(docs) < limit:
        break
      query = query.limit(limit).offset(len(all_docs))
    return all_docs

  @classmethod
  def delete_by_id(cls, object_id):
    """
    Permanently delete an object by primary key.
    """
    try:
      obj = cls.get_by_id(object_id)
      obj.delete_instance()
    except DoesNotExist:
      raise ResourceNotFoundException(f"{cls.__name__} with id {object_id} not found")

  @classmethod
  def validate(cls, instance) -> Tuple[bool, List[str]]:
    """
    Validate the fields of the instance.
    """
    errors = []
    valid = True
    for field_name, field_obj in instance._meta.fields.items():
      value = getattr(instance, field_name, None)
      if field_obj.null is False and value is None:
        valid = False
        errors.append(f"Field '{field_name}' cannot be null.")
    return valid, errors
