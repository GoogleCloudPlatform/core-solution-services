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

from common.orm_config import ORM_MODE, SQL_ORM, FIRESTORE_ORM

from .base_model import *

if ORM_MODE == SQL_ORM:

  from .base_model_sql import *
  from .user_sql import *
  from .llm_sql import *
  from .llm_query_sql import *
  from .batch_job_sql import *
  from .session_sql import *

else: # ORM_MODE == FIRESTORE_ORM

  from .node_item import *
  from .user import *
  from .user_event import *
  from .learning_record import *
  from .llm import *
  from .llm_query import *
  from .agent import *
  from .custom_fields import *
  from .batch_job import *
  from .session import *
  from .staff import *
