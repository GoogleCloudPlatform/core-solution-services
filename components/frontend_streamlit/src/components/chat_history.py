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
Chat history panel for UI
"""

import streamlit as st
from common.utils.logging_handler import Logger
from api import get_all_chats, delete_chat
from styles.chat_history_styles import history_styles
import utils

Logger = Logger.get_logger(__file__)

def get_agent_chats(selected_agent):
  """
  List all chat history for a given agent
  """
  index = 0
  Logger.info(f"get_chat_agents with {selected_agent}")
  for user_chat in (st.session_state.user_chats or []):

    first_history_item = user_chat["history"][0]
    if "HumanInput" in first_history_item:
      first_question = first_history_item["HumanInput"][:50]
      if len(first_history_item["HumanInput"]) > 60:
        first_question = first_question + "..."
    else:
      first_question = "Chat (No question)"

    chat_id = user_chat["id"]
    if "agent_name" in user_chat and (
      selected_agent in (user_chat["agent_name"], "All")):
      agent_name = user_chat.get("agent_name", None)
      agent_name_str = f"**{agent_name}:** " if agent_name else ""

      with st.container():
        select_chat = st.button(f"{agent_name_str}{first_question}",
                                use_container_width=True,
                                key=f"{agent_name}{index}")
        if select_chat:
          st.session_state.agent_name = agent_name
          st.session_state.chat_id = chat_id
          st.session_state.landing_user_input = None
          utils.navigate_to("Chat")
    index += 1

def chat_history_panel():
  """
  List agent options for retrieving chat history
  """
  history_styles()

  st.session_state.user_chats = get_all_chats(
      auth_token=st.session_state.auth_token)

  with st.sidebar:
    col1, col2, col3 = st.columns([3, 3, 2])
    with col1:
      st.subheader("Recent")
    with col2:
      new_chat_button = st.button("New Chat", key="new chat")
      if new_chat_button:
        utils.reset_session_state()
        utils.navigate_to("Chat")
    with col3:
      clear_chats_button = st.button("Clear", key="clear chat")
      if clear_chats_button:
        clear_chat_history()
        utils.reset_session_state()
        utils.navigate_to("Landing")

    all_agents = set()

    # Iterate through all chats and get available agents
    for user_chat in (st.session_state.user_chats or []):
      all_agents.add(user_chat["agent_name"])
    agent_options = list(all_agents)
    agent_options.insert(0, "All")

    # Add agent options to dropdown
    select_agent = st.selectbox("Filter by Agent", agent_options, key="agent0")
    get_agent_chats(select_agent)


def clear_chat_history():
  """
  Clear user chat history by deleting all chats
  """
  for user_chat in (st.session_state.user_chats or []):
    delete_chat(user_chat["id"])
