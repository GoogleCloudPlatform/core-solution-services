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
from api import get_all_query_engines
from components.chat_history import chat_history_panel
from common.utils.logging_handler import Logger
import utils

Logger = Logger.get_logger(__file__)

def landing_page():
  st.title("Welcome.")
  chat_history_panel()

  start_chat, start_query, build_query = st.columns((1, 1, 1))

  with start_chat:
    with st.container():
      "Start a Chat with"
      agent_name = st.selectbox(
          "Agent:",
          ("Chat", "Plan"))
      chat_button = st.button("Start", key=2)
      if chat_button:
        st.session_state.agent_name = agent_name
        st.session_state.chat_id = None
        utils.navigate_to("Chat")

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
        "Start a Query with"
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

  with build_query:
    with st.container():
      "Managing Query Engines"
      build_button = st.button("Start", key=4)
      if build_button:
        utils.navigate_to("Query_Engines")


if __name__ == "__main__":
  #./main.py is used as an entrypoint for the build,
  # which creates a page that duplicates the Login page named "main".
  utils.hide_pages(["main"])
  utils.init_api_base_url()
  landing_page()
