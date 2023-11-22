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
from api import get_all_chats
import utils
from config import APP_BASE_PATH

Logger = Logger.get_logger(__file__)

CHAT_HISTORY_LIST_STYLE = """
<style>
  [data-testid=stSidebar] {
    .stButton button {
      @media screen and (prefers-color-scheme: dark) {
        background-color: #195;
      }
      display: block !important;
      font-weight: bold;
      border: 0px;
      text-align: left;
      border-radius: 10px;
    }

    .stButton button:hover {
      background-color:#d3d3d3;
      color: black;
      border-radius: 10px;
      text-align: left;
    }
  }
</style>
"""

def get_agent_chats(selected_agent):
  """
  List all chat history for a given agent
  """
  index = 0
  for user_chat in (st.session_state.user_chats or []):
    first_question = user_chat["history"][0]["HumanInput"][:50]
    if len(user_chat["history"][0]["HumanInput"]) > 60:
      first_question = first_question + "..."

    chat_id = user_chat["id"]
    if "agent_name" in user_chat and (
      selected_agent in (user_chat["agent_name"], "All")):
      agent_name = user_chat["agent_name"]
      with st.container():
        select_chat = st.button(f"**{agent_name}**: {first_question}",
                                use_container_width=True,
                                key=f"{agent_name}{index}")
        if select_chat:
          utils.navigate_to(
            f"{APP_BASE_PATH}/Chat?chat_id={chat_id}&agent_name={agent_name}&" \
            f"auth_token={st.session_state.auth_token}")
    index += 1

def chat_history_panel():
  """
  List agent options for retrieving chat history
  """
  st.session_state.user_chats = get_all_chats(
      auth_token=st.session_state.auth_token)
  css = CHAT_HISTORY_LIST_STYLE
  st.markdown(css, unsafe_allow_html=True)

  with st.sidebar:
    st.header("My Chats")
    all_agents = set()

    # Iterate through all chats and get available agents
    for user_chat in (st.session_state.user_chats or []):
      all_agents.add(user_chat["agent_name"])
    agent_options = list(all_agents)
    agent_options.insert(0, "All")

    # Add agent options to dropdown
    select_agent = st.selectbox("Filter by Agent:", agent_options, key="agent0")
    get_agent_chats(select_agent)
