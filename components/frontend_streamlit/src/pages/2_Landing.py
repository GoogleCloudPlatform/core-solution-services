# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
  Streamlit app Landing Page
"""
# pylint: disable=invalid-name,pointless-string-statement,unused-variable
import streamlit as st
from api import get_all_query_engines, get_all_chat_llm_types
from components.chat_history import chat_history_panel
from common.utils.logging_handler import Logger
import utils

Logger = Logger.get_logger(__file__)


LANDING_PAGE_STYLES = """
<style>
  .stButton[data-testid="stFormSubmitButton"] {
    display: none;
  }
</style>
"""


def landing_page():
  """
  Landing Page
  """
  chat_history_panel()

  # Clean up session.
  utils.reset_session_state()

  chat_llm_types = get_all_chat_llm_types()

  st.markdown(LANDING_PAGE_STYLES, unsafe_allow_html=True)

  st.title("Hello again.")
  st.subheader("You can ask me anything:")

  with st.form("user_input_form", border=False, clear_on_submit=True):
    col1, col2, col3 = st.columns([5, 3, 2])
    with col1:
      user_input = st.text_input("")
      submitted = st.form_submit_button("Submit")
    with col2:
      st.session_state.chat_llm_type = st.selectbox(
          "Model", chat_llm_types)
    with col3:
      st.session_state.default_route = st.selectbox(
          "Chat Mode", ["Auto", "Chat", "Plan", "Query"])

    if submitted:
      utils.reset_session_state()
      st.session_state.landing_user_input = user_input
      utils.navigate_to("Chat")

  st.divider()

  st.subheader("Or run with a specific Agent or Task:")
  start_chat, start_query = st.columns((1, 1))

  with start_chat:
    with st.container():
      agent_name = st.selectbox(
          "Agent:",
          ("Chat", "Plan"))
      chat_button = st.button("Start", key=2)
      if chat_button:
        st.session_state.agent_name = agent_name
        st.session_state.chat_id = None
        utils.navigate_to("Agent")

  with start_query:
    # Get all query engines as a list
    query_engine_list = get_all_query_engines(
      auth_token=st.session_state.auth_token)

    if query_engine_list is None or len(query_engine_list) == 0:
      with st.container():
        "No Query Engines"
    else:
      query_engines = {}
      for item in query_engine_list:
        query_engines[item["name"]] = item

      Logger.info(query_engines)
      with st.container():
        qe_name = st.selectbox(
            "Query Engine:",
            tuple(query_engines.keys()))
        query_button = st.button("Start", key=3)
        query_engine_id = query_engines[qe_name]["id"]
        st.session_state.query_engine_id = query_engine_id
        if query_button:
          st.session_state.agent_name = agent_name
          st.session_state.chat_id = None
          utils.navigate_to("Query")

if __name__ == "__main__":
  utils.init_page()
  landing_page()
