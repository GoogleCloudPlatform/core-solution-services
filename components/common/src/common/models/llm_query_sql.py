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
SQL Models for LLM Query Engines
"""
from typing import List
from peewee import (UUIDField,
                    DateTimeField,
                    TextField,
                    IntegerField,
                    BooleanField,
                    TimestampField)
from playhouse.postgres_ext import ArrayField, JSONField
from common.models.base_model_sql import SQLBaseModel
from common.models.llm_query import UserQueryUtil, QueryReferenceUtil


class UserQuery(SQLBaseModel, UserQueryUtil):
  """
  UserQuery SQL ORM class
  """
  id = UUIDField()
  user_id = TextField()
  title = TextField(null=True)
  query_engine_id = TextField()
  prompt = TextField()
  response = TextField(null=True)
  history = ArrayField(default=[])

  @classmethod
  def find_by_user(cls,
                   userid,
                   skip=0,
                   order_by="-created_time",
                   limit=1000):
    """
    Fetch all queries for user

    Args:
        userid (str): User id
        skip (int, optional): number of chats to skip.
        order_by (str, optional): order list according to order_by field.
        limit (int, optional): limit till cohorts to be fetched.

    Returns:
        List[UserQuery]: List of queries for user.

    """
    pass



class QueryEngine(SQLBaseModel):
  """
  QueryEngine ORM class
  """
  id = UUIDField()
  name = TextField()
  query_engine_type = TextField()
  description = TextField(default="")
  llm_type = TextField(null=True)
  embedding_type = TextField()
  vector_store = TextField(null=True)
  created_by = TextField()
  is_public = BooleanField(default=False)
  index_id = TextField(null=True)
  index_name = TextField(null=True)
  endpoint = TextField(null=True)
  doc_url = TextField(null=True)
  agents = ArrayField(null=True)
  parent_engine_id = TextField(null=True)
  manifest_url = TextField(null=True)
  params = JSONField(default={})


  @classmethod
  def find_by_name(cls, name):
    """
    Fetch a specific query engine by name

    Args:
        name (str): Query engine name

    Returns:
        QueryEngine: query engine object

    """
    pass


  @classmethod
  def find_children(cls, q_engine) -> List[BaseModel]:
    """
    Find all child engines for an engine.

    Returns:
        List of QueryEngine objects that point to this engine as parent

    """
    pass


class QueryReference(SQLBaseModel, QueryReferenceUtil):
  """
  QueryReference ORM class. This class represents a single query reference.
  It points to a specific chunk of text in one of the indexed documents.

  """
  id = UUIDField()  # All modalities
  query_engine_id = TextField()  # All modalities
  query_engine = TextField()  # All modalities
  document_id = TextField()  # All modalities
  document_url = TextField()  # All modalities
  modality = TextField()  # All modalities: text image video audio
  chunk_id = TextField(null=True)  # All modalities
  chunk_url = TextField(null=True)  # Image or video or audio only
  page = IntegerField(null=True)  # Text or image only
  document_text = TextField(null=True)  # Text only
  timestamp_start = IntegerField(null=True)  # Video or audio only
  timestamp_stop = IntegerField(null=True)  # Video or audio only


class QueryResult(SQLBaseModel):
  """
  QueryResult ORM class.  Each query result consists of a text query
  response and a list of links to source query documents, as a
  list of query reference ids.
  """
  id = UUIDField()
  query_engine_id = TextField()
  query_engine = TextField()
  query_refs = ArrayField(default=[])
  response = TextField()


class QueryDocument(SQLBaseModel):
  """
  QueryDocument ORM class.
  """
  id = UUIDField()
  query_engine_id = TextField()
  query_engine = TextField()
  doc_url = TextField()
  index_file = TextField(null=True)
  index_start = IntegerField(null=True)
  index_end = IntegerField(null=True)
  metadata = JSONField(null=True)


  @classmethod
  def find_by_query_engine_id(cls,
                              query_engine_id,
                              skip=0,
                              order_by="-created_time",
                              limit=1000):
    """
    Fetch all QueryDocuments for query engine

    Args:
        query_engine_id (str): Query Engine id
        skip (int, optional): number of urls to skip.
        order_by (str, optional): order list according to order_by field.
        limit (int, optional): limit till cohorts to be fetched.

    Returns:
        List[QueryDocument]: List of QueryDocuments

    """
    pass

  @classmethod
  def find_by_url(cls, query_engine_id, doc_url):
    """
    Fetch a document by url

    Args:
        query_engine_id (str): Query Engine id
        doc_url (str): Query document url

    Returns:
        QueryDocument: query document object

    """
    pass

  @classmethod
  def find_by_index_file(cls, query_engine_id, index_file):
    """
    Fetch a document by url

    Args:
        query_engine_id (str): Query Engine id
        doc_url (str): Query document url

    Returns:
        QueryDocument: query document object

    """
    pass


class QueryDocumentChunk(SQLBaseModel):
  """
  QueryDocumentChunk ORM class.
  """
  id = UUIDField()  # All modalities
  query_engine_id = TextField()  # All modalities
  query_document_id = TextField()  # All modalities
  index = IntegerField()  # All modalities
  modality = TextField()  # All modalities: text image video audio
  page = IntegerField(null=True)  # Text or image only
  chunk_url = TextField(null=True)  # Image or video or audio only
  text = TextField(null=True)  # Text only
  clean_text = TextField(null=True)  # Text only (optional)
  sentences = ArrayField(null=True)  # Text only (optional)
  timestamp_start = IntegerField(null=True)  # Video or audio only
  timestamp_stop = IntegerField(null=True)  # Video or audio only


  @classmethod
  def find_by_index(cls, query_engine_id, index):
    """
    Fetch a document chunk for a query engine by index

    Args:
        query_engine_id (str): Query engine id
        index (int): QueryDocumentChunk index

    Returns:
        QueryDocumentChunk: query document chunk object

    """
    pass
