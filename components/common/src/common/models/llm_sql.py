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
SQL Models for LLM generation and chat
"""
import uuid
from peewee import TextField, fn
from playhouse.postgres_ext import ArrayField
from common.models.base_model_sql import SQLBaseModel
from common.models.llm import UserChatUtil


class UserChat(SQLBaseModel, UserChatUtil):
  """
  UserChat ORM class
  """
  id = TextField(primary_key=True, default=str(uuid.uuid4))
  user_id = TextField()
  prompt = TextField(default="")
  title = TextField(default="")
  llm_type = TextField(null=True)
  agent_name = TextField(null=True)
  history = ArrayField(default=[])

  @classmethod
  def find_by_user(cls,
                   user_id,
                   skip=0,
                   order_by="-created_time",
                   limit=1000):
    """
    Fetch all chats for user

    Args:
        user_id (str): User id
        skip (int, optional): number of chats to skip.
        order_by (str, optional): order list according to order_by field.
        limit (int, optional): limit till cohorts to be fetched.

    Returns:
        List[UserChat]: List of chats for user.

    """
    objects = cls.select().where(
      (cls.user_id == user_id) &
      (cls.deleted_at_timestamp is None)
    ).order_by(
      fn.datetime(getattr(cls, order_by[1:]), "UTC")
      if order_by.startswith("-") else
      fn.datetime(getattr(cls, order_by), "UTC")
    ).offset(skip).limit(limit)
    return list(objects)
