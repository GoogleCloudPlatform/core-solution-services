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
Center content for landing page
"""

import streamlit as st
from api import get_all_query_engines
import utils

#from components.task_picker import task_picker_display

def landing_suggestions():
  info, plan, chat, query = st.columns(4)

  with info:
    with st.container(border=True):
      any_button = st.button("Specify task", type="secondary")
      st.caption("Click here to pick any task.")
      if any_button:
        task_picker_display()

  with plan:
    with st.container(border=True):
      plan_button = st.button("Plan", type="primary", use_container_width=True)
      st.caption("Generate and execute a plan to your specification.")
      if plan_button:
        st.switch_page("pages/4_Agent.py")

  with chat:
    with st.container(border=True):
      chat_button = st.button("Chat", type="primary", use_container_width=True)
      st.caption("Get answers with a standard prompt.")
      if chat_button:
        st.switch_page("pages/3_Chat.py")

  with query:
    with st.container(border=True):
      query_button = st.button("Query", type="primary",
                               use_container_width=True)
      st.caption("Utilize a data source to get answers.")
      if query_button:
        st.switch_page("pages/4_Query.py")


def task_picker_display():
  agent_name = st.selectbox(
      "Agent:",
      ("Chat", "Plan"))
  chat_button = st.button("Start", key=2)
  if chat_button:
    st.session_state.agent_name = agent_name
    st.session_state.chat_id = None
    utils.navigate_to("Chat")

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
