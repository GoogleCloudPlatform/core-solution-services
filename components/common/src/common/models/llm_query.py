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
Models for LLM Query Engines
"""
from typing import List
from fireo.fields import (TextField, ListField, IDField,
                          BooleanField, NumberField, MapField)
from common.models import BaseModel

# pylint: disable = access-member-before-definition

# constants used as tags for query history
QUERY_HUMAN = "HumanQuestion"
QUERY_AI_RESPONSE = "AIResponse"
QUERY_AI_REFERENCES = "AIReferences"

# query engine types
QE_TYPE_VERTEX_SEARCH = "qe_vertex_search"
QE_TYPE_LLM_SERVICE = "qe_llm_service"
QE_TYPE_INTEGRATED_SEARCH = "qe_integrated_search"

class UserQueryUtil():
  """ Utility class for UserQuery """

  def __init__(self):
    self.history = None

  def update_history(self, prompt: str=None,
                     response: str=None,
                     references: List[dict]=None,
                     custom_entry=None):
    """ Update history with query and response """
    if not self.history:
      self.history = []

    if prompt:
      self.history.append({QUERY_HUMAN: prompt})

    if response:
      self.history.append({QUERY_AI_RESPONSE: response})

    if references:
      self.history.append({QUERY_AI_REFERENCES: references})

    if custom_entry:
      self.history.append(custom_entry)

    self.save(merge=True)

  @classmethod
  def is_human(cls, entry: dict) -> bool:
    return QUERY_HUMAN in entry.keys()

  @classmethod
  def is_ai(cls, entry: dict) -> bool:
    return QUERY_AI_RESPONSE in entry.keys()

  @classmethod
  def entry_content(cls, entry: dict) -> str:
    return list(entry.values())[0]

  def save(self, merge=True):
    raise NotImplementedError("Save method should be implemented in the subclass")


class UserQuery(BaseModel, UserQueryUtil):
  """
  UserQuery ORM class
  """
  id = IDField()
  user_id = TextField(required=True)
  title = TextField(required=False)
  query_engine_id = TextField(required=True)
  prompt = TextField(required=True)
  response = TextField(required=False)
  history = ListField(default=[])

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "user_queries"

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
    objects = cls.collection.filter(
        "user_id", "==", userid).filter(
            "deleted_at_timestamp", "==",
            None).order(order_by).offset(skip).fetch(limit)
    return list(objects)


class QueryEngine(BaseModel):
  """
  QueryEngine ORM class
  """
  id = IDField()
  name = TextField(required=True)
  query_engine_type = TextField(required=True)
  description = TextField(required=True, default="")
  llm_type = TextField(required=False)
  embedding_type = TextField(required=True)
  vector_store = TextField(required=False)
  created_by = TextField(required=True)
  is_public = BooleanField(default=False)
  index_id = TextField(required=False)
  index_name = TextField(required=False)
  endpoint = TextField(required=False)
  doc_url = TextField(required=False)
  agents = ListField(required=False)
  parent_engine_id = TextField(required=False)
  manifest_url = TextField(required=False)
  params = MapField(default={})

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "query_engines"

  @classmethod
  def find_by_name(cls, name):
    """
    Fetch a specific query engine by name

    Args:
        name (str): Query engine name

    Returns:
        QueryEngine: query engine object

    """
    q_engine = cls.collection.filter(
        "name", "==", name).filter(
            "deleted_at_timestamp", "==",
            None).get()
    return q_engine

  @classmethod
  def find_children(cls, q_engine) -> List[BaseModel]:
    """
    Find all child engines for an engine.

    Returns:
        List of QueryEngine objects that point to this engine as parent

    """
    q_engines = cls.collection.filter(
        "parent_engine_id", "==", q_engine.id).filter(
            "deleted_at_timestamp", "==",
            None).fetch()
    return list(q_engines)

  @property
  def deployed_index_name(self):
    return f"deployed_{self.index_name}"


class QueryReferenceUtil():
  """ Utility class for QueryReference """

  def __repr__(self) -> str:
    """
    Log-friendly string representation of a QueryReference
    """
    if self.modality.casefold()=="text":
      document_text_num_tokens = len(self.document_text.split())
      document_text_num_chars = len(self.document_text)
      document_text_snippet = self.document_text[:min(100,
                                                      document_text_num_chars)]
      chunk_url = None
    else:
      document_text_num_tokens = None
      document_text_num_chars = None
      document_text_snippet = None
      chunk_url = self.chunk_url
    return (
      f"Query_Ref(query_engine_name={self.query_engine}, "
      f"document_id={self.document_id}, "
      f"document_url={self.document_url}, "
      f"chunk_id={self.chunk_id}, "
      f"chunk_url={chunk_url}, "
      f"modality={self.modality}, "
      f"page={self.page}, "
      f"chunk_num_tokens={document_text_num_tokens}, "
      f"chunk_num_chars={document_text_num_chars}, "
      f"chunk_text={document_text_snippet}, "
      f"linked_ids={self.linked_ids})"
    )

class QueryReference(BaseModel, QueryReferenceUtil):
  """
  QueryReference ORM class. This class represents a single query reference.
  It points to a specific chunk of text in one of the indexed documents.

  """
  id = IDField()  # All modalities
  query_engine_id = TextField(required=True)  # All modalities
  query_engine = TextField(required=True)  # All modalities
  document_id = TextField(required=True)  # All modalities
  document_url = TextField(required=True)  # All modalities
  modality = TextField(required=True)  # All modalities: text image video audio
  chunk_id = TextField(required=False)  # All modalities
  chunk_url = TextField(
      required=False, default=None)  # Image or video or audio only
  page = NumberField(required=False, default=None)  # Text or image only
  document_text = TextField(required=False, default=None)  # Text only
  timestamp_start = NumberField(
      required=False, default=None)  # Video or audio only
  timestamp_stop = NumberField(
      required=False, default=None)  # Video or audio only

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "query_references"


class QueryResult(BaseModel):
  """
  QueryResult ORM class.  Each query result consists of a text query
  response and a list of links to source query documents, as a
  list of query reference ids.
  """
  id = IDField()
  query_engine_id = TextField(required=True)
  query_engine = TextField(required=True)
  query_refs = ListField(default=[])
  response = TextField(required=True)

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "query_results"


class QueryDocument(BaseModel):
  """
  QueryDocument ORM class.
  """
  id = IDField()
  query_engine_id = TextField(required=True)
  query_engine = TextField(required=True)
  doc_url = TextField(required=True)
  index_file = TextField(required=False)
  index_start = NumberField(required=False)
  index_end = NumberField(required=False)
  metadata = MapField(required=False)

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "query_documents"

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
    objects = cls.collection.filter(
      "query_engine_id", "==", query_engine_id).filter(
      "deleted_at_timestamp", "==",
      None).order(order_by).offset(skip).fetch(limit)
    return list(objects)

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
    q_doc = cls.collection.filter(
      "query_engine_id", "==", query_engine_id).filter(
      "doc_url", "==", doc_url).filter(
          "deleted_at_timestamp", "==",
          None).get()
    return q_doc

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
    q_doc = cls.collection.filter(
      "query_engine_id", "==", query_engine_id).filter(
      "index_file", "==", index_file).filter(
          "deleted_at_timestamp", "==",
          None).get()
    return q_doc


class QueryDocumentChunk(BaseModel):
  """
  QueryDocumentChunk ORM class.
  """
  id = IDField()  # All modalities
  query_engine_id = TextField(required=True)  # All modalities
  query_document_id = TextField(required=True)  # All modalities
  index = NumberField(required=True)  # All modalities
  modality = TextField(required=True)  # All modalities: text image video audio
  page = NumberField(required=False, default=None)  # Text or image only
  chunk_url = TextField(
    required=False, default=None)  # Image or video or audio only
  text = TextField(required=False, default=None)  # Text only
  clean_text = TextField(required=False, default=None)  # Text only (optional)
  sentences = ListField(required=False, default=None)  # Text only (optional)
  timestamp_start = NumberField(
    required=False, default=None)  # Video or audio only
  timestamp_stop = NumberField(
    required=False, default=None)  # Video or audio only
  linked_ids = ListField(
    IDField(), required=False, default=None)  # All modalities

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "query_document_chunks"

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
    q_chunk = cls.collection.filter(
        "query_engine_id", "==", query_engine_id).filter(
            "index", "==", index).filter(
            "deleted_at_timestamp", "==",
            None).get()
    return q_chunk
