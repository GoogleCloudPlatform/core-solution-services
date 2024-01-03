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
Start a specific chat or run specific query
"""

import streamlit as st
from api import get_all_query_engines
import utils

def task_picker_display():
  with st.container():
    agent_name = st.selectbox(
        "Agent:",
        ("Chat", "Plan"))
    chat_button = st.button("Start", key=2)
    if chat_button:
      st.session_state.agent_name = agent_name
      st.session_state.chat_id = None
      utils.navigate_to("Agent")

  # Get all query engines as a list
  query_engine_list = get_all_query_engines(
    auth_token=st.session_state.auth_token)

  if query_engine_list is None or len(query_engine_list) == 0:
    with st.container():
      st.text("No Query Engines")
  else:
    query_engines = {}
    for item in query_engine_list:
      query_engines[item["name"]] = item

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
