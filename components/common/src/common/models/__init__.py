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
Flatten import namespace for models
"""

from common.config import ORM_MODE, SQL_ORM, FIRESTORE_ORM

from .base_model import BaseModel

if ORM_MODE == SQL_ORM:

  from .base_model_sql import SQLBaseModel
  from .user_sql import User
  from .llm_sql import UserChat
  from .llm_query_sql import QueryEngine, QueryReference, QueryResult, QueryDocument, QueryDocumentChunk
  from .batch_job_sql import BatchJobModel
  from .session_sql import Session

else: # ORM_MODE == FIRESTORE_ORM

  from .node_item import NodeItem
  from .user import User
  from .user_event import UserEvent
  from .learning_record import LearningRecord
  from .llm import UserChat
  from .llm_query import QueryEngine, QueryReference, QueryResult, QueryDocument, QueryDocumentChunk
  from .agent import Agent
  from .custom_fields import GCSPathField
  from .batch_job import BatchJobModel
  from .session import Session
  from .staff import Staff
