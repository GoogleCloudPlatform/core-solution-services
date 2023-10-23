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
Models for LLM generation and chat
"""
from typing import List
from fireo.fields import TextField, ListField, IDField
from common.models import BaseModel
from langchain.schema import HumanMessage, AIMessage

# constants used as tags for chat history
CHAT_HUMAN = "HumanInput"
CHAT_AI = "AIOutput"


class UserChat(BaseModel):
  """
  UserChat ORM class
  """
  id = IDField()
  user_id = TextField(required=True)
  title = TextField(required=False)
  llm_type = TextField(required=True)
  agent_name = TextField(required=False)
  history = ListField(default=[])

  class Meta:
    ignore_none_field = False
    collection_name = BaseModel.DATABASE_PREFIX + "user_chats"

  @classmethod
  def find_by_user(cls,
                   userid,
                   skip=0,
                   order_by="-created_time",
                   limit=1000):
    """
    Fetch all chats for user

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

  @property
  def langchain_chat_history(self):
    langchain_history = []
    for entry in self.history:
      content = UserChat.entry_content(entry)
      if self.is_human(entry):
        langchain_history.append(HumanMessage(content=content))
      elif self.is_ai(entry):
        langchain_history.append(AIMessage(content=content))
    return langchain_history
    
  @classmethod
  def get_history_entry(cls, prompt: str, response: str) -> List[dict]:
    """ Get history entry for query and response """
    entry = [{CHAT_HUMAN: prompt}, {CHAT_AI: response}]
    return entry

  def update_history(self, prompt: str, response: str):
    """ Update history with query and response """
    entry = self.get_history_entry(prompt, response)
    self.history.extend(entry)
    self.save(merge=True)

  @classmethod
  def is_human(cls, entry: dict) -> bool:
    return CHAT_HUMAN in entry.keys()

  @classmethod
  def is_ai(cls, entry: dict) -> bool:
    return CHAT_AI in entry.keys()

  @classmethod
  def entry_content(cls, entry: dict) -> str:
    return list(entry.values())[0]
