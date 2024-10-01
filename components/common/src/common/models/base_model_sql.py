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
from common.config import PG_HOST, PG_DBNAME, PG_USER, PG_PASSWD
from common.utils.errors import ResourceNotFoundException
from peewee import Model, DateTimeField, TextField
from playhouse.postgres_ext import PostgresqlExtDatabase

# instantiate connection to postgres db
db = PostgresqlExtDatabase(PG_DBNAME,
                           host=PG_HOST,
                           password=PG_PASSWD,
                           user=PG_USER)

class SQLBaseUtility:
  
  def filter(filterExpr: str) -> SQLBaseModel:
    pass


class SQLBaseModel(Model):
  """
  BaseModel for SQL-based data models
  """
  created_time = DateTimeField()
  last_modified_time = DateTimeField()
  deleted_at_timestamp = DateTimeField(default=None)
  deleted_by = TextField(default="")
  archived_at_timestamp = DateTimeField(default=None)
  archived_by = TextField(default="")
  created_by = TextField(default="")
  last_modified_by = TextField(default="")

  collection = SQLBaseUtility()

  class Meta:
    database = db

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
      obj = cls.select().where(cls.id == doc_id).get()
    except peewee.DoesNotExist:
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
    cls.delete().where(cls.id == doc_id)

  @classmethod
  def soft_delete_by_id(cls, object_id, by_user=None):
    """Soft delete an object by id
      Args:
          object_id (str): unique id
          by_user
      Raises:
          ResourceNotFoundException: If the object does not exist
      """
    obj = cls.find_by_id(object_id)
    if obj is None:
      raise ResourceNotFoundException(
          f"{cls.__name__} with id {object_id} is not found")
    obj.update({obj.deleted_at_timestamp: datetime.datetime.utcnow(),
                obj.deleted_by: by_user})

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
    objs = cls.select().order_by(cls.created_time.desc())

  def get_fields(self, reformat_datetime=False, remove_meta=False):
    """
    """
    field_names = cls._meta.sorted_field_names
    field_dict = {
      field: cls.getattr(field)
      for field in field_names
    }

  def validate(self) -> Tuple[bool, List[str]]:
    """
    Validate a model in this class.

    Returns:
      True,[] or False, list of error messages
    """
    pass
