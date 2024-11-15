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
from common.config import PG_HOST, PG_DBNAME, PG_USER, PG_PASSWD
from common.utils.errors import ResourceNotFoundException
from peewee import Model, DoesNotExist, DateTimeField, TextField
from playhouse.postgres_ext import PostgresqlExtDatabase

# pylint: disable = protected-access, arguments-renamed

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

  def __init__(self, *args, **kwargs):
    super().__init__(args, kwargs)

  @property
  def id(self):
    """
    Returns the value of the primary key field.
    """
    return getattr(self, self._meta.primary_key.name) # noqa

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
      if key in instance.__data__:
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
    class_meta = cls._meta # noqa
    primary_key_field = class_meta.primary_key.name
    try:
      return cls.get(
        (getattr(cls, primary_key_field) == doc_id) &
        (cls.deleted_at_timestamp.is_null())
      )
    except DoesNotExist as exc:
      raise ResourceNotFoundException(
        f"{class_meta.table_name} with id {doc_id} is not found") from exc

  def save(self, force_insert=False, only=None, merge=None):
    """
    Overrides default method to save items with timestamp
    Args:
      force_insert (bool): If True, forces an INSERT statement
      only (list or tuple): A list of field instances to save
      merge (bool, optional): If specified, performs a get_or_create-style save
    Returns:
      The saved instance
    """
    class_meta = self._meta # noqa
    primary_key_field = class_meta.primary_key.name
    try:
      # Update timestamps
      date_timestamp = datetime.datetime.utcnow()
      if not self.id:
        print("Generating ID value")
        self.created_time = date_timestamp
        setattr(self, primary_key_field, str(uuid.uuid4()))
      self.last_modified_time = date_timestamp

      if merge:
        print("MERGE MODE")
        fields = self._meta.fields.keys() # noqa
        if only:
          fields = [field.name for field in only]
        query_data = {field: getattr(self, field) for field in fields}

        # Perform the get_or_create operation
        instance, created = self.__class__.get_or_create(
          defaults=query_data, **query_data
        )

        # Update existing instance's fields if not created
        if not created:
          for field in fields:
            setattr(instance, field, getattr(self, field))
          # Save the updated instance
          instance._saving = True  # Prevent recursion during save
          instance.save(only=fields)
          instance._saving = False  # Clear the flag after saving

        return instance

      else:
        print("NON MERGE MODE")
        print(f"Attempting to save: {self.__class__.__name__} "
              f"with id {self.id}")
        print(f"Data to save: {self.__data__}")

        # Call the super save method
        result = super().save(force_insert=force_insert, only=only)
        if result is None:
          print("Super save returned None. Check the model and database connection.")
        print("Exiting save()")
        return result

    except Exception as e:
      print("Error during super().save():", str(e))
      raise

  def update1(self): # noqa
    """
    Instance-level update method:
    Updates the current instance and saves the changes to the database.
    """
    # Debug print to check state before saving
    print("Before update, instance state:", self.__dict__)

    try:
      # Make sure to only save fields that have changed
      fields_to_update = self.__dict__.get("_dirty")
      print("Fields to update:", fields_to_update)
      self.save(only=fields_to_update)
      _ = super().update()

      print("Update successful")
    except Exception as e:
      print(f"Update failed: {e}")
      raise

  @classmethod
  def delete_by_id(cls, pk):
    """Deletes from the Database the object of this type by id (not key)
    Args:
      pk (string): the document id without collection_name
      (i.e. not the key)
    """
    class_meta = cls._meta # noqa
    return cls.delete().where(class_meta.primary_key.name == pk).execute()

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

  def get_fields(self, reformat_datetime=False, remove_meta=False):
    """
    Overrides default method to fix data type for datetime fields.
    remove_meta=True will remove extra meta data fields (useful for testing)
    """
    fields = {}
    for field_name in self._meta.sorted_field_names: # noqa
      field_value = getattr(self, field_name)
      if isinstance(field_value, datetime.datetime) and reformat_datetime:
        field_value = str(field_value)
      fields[field_name] = field_value
    if remove_meta:
      fields = self.remove_field_meta(fields)
    # fields["id"] = getattr(self, self._meta.primary_key.name)
    fields["id"] = self.id
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
