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
Models for Agents
"""
from __future__ import annotations
from enum import Enum
from fireo.fields import TextField, IDField, ListField
from common.models.base_model import BaseModel


class AgentType(str, Enum):
  """ Enum class for Agent types """
  LANGCHAIN_CONVERSATIONAL = "langchain_Conversational"
  LANGCHAIN_ZERO_SHOT = "langchain_ZeroShot"
  LANGCHAIN_CONVERSATIONAL_CHAT = "langchain_ConversationalChat"

  @classmethod
  def is_langchain(cls, agent_type: AgentType):
    return agent_type.value.startswith("langchain")


class AgentCapability(str, Enum):
  """ Enum class for Agent capabilities """
  CHAT = "Chat"
  QUERY = "Query"
  TASK = "Task"
  PLAN = "Plan"
  DATABASE = "Database"
  ROUTE = "Route"


class Agent(BaseModel):
  """
  Agent ORM class
  """
  id = IDField()
  name = TextField(required=True)
  user_id = TextField(required=False)
  agent_type = TextField(required=True)
  llm_type = TextField(required=True)
  capabilities = ListField(required=True)
  tools = ListField()

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "agents"

  @classmethod
  def find_by_user(cls,
                   userid,
                   skip=0,
                   order_by="-created_time",
                   limit=1000):
    """
    Fetch all agents for user

    Args:
        userid (str): User id
        skip (int, optional): number of chats to skip.
        order_by (str, optional): order list according to order_by field.
        limit (int, optional): limit till cohorts to be fetched.

    Returns:
        List[UserChat]: List of chats for user.

    """
    objects = cls.collection.filter(
        "user_id", "==", userid).filter(
            "deleted_at_timestamp", "==",
            None).order(order_by).offset(skip).fetch(limit)
    return list(objects)

  @classmethod
  def find_by_name(cls, name):
    """
    Fetch agent by name

    Args:
        name (str): Agent name

    Returns:
        Agent or None if not found

    """
    obj = cls.collection.filter(
        "name", "==", name).filter(
        "deleted_at_timestamp", "==",
        None).get()
    return obj


class UserPlan(BaseModel):
  """
  User Plan ORM class
  """
  id = IDField()
  name = TextField()
  user_id = TextField(required=True)
  task_prompt = TextField(required=True)
  task_response = TextField(required=True)
  agent_name = TextField(required=True)
  plan_steps = ListField() # list of plan step ids

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "user_plans"

  @classmethod
  def find_by_user(cls,
                   userid,
                   skip=0,
                   order_by="-created_time",
                   limit=1000):
    """
    Fetch all plans for user

    Args:
        userid (str): User id
        skip (int, optional): number of plans to skip.
        order_by (str, optional): order list according to order_by field.
        limit (int, optional): limit till cohorts to be fetched.

    Returns:
        List[UserPlan]: List of plans for user.

    """
    objects = cls.collection.filter(
        "user_id", "==", userid).filter(
            "deleted_at_timestamp", "==",
            None).order(order_by).offset(skip).fetch(limit)
    return list(objects)


class PlanStep(BaseModel):
  """
  Plan Step ORM class
  """
  id = IDField()
  user_id = TextField(required=True)
  agent_name = TextField(required=True)
  plan_id = TextField(required=True)
  description = TextField(required=True)

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "plan_steps"
