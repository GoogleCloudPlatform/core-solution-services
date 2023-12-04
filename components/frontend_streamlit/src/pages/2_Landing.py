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
from config import APP_BASE_PATH

Logger = Logger.get_logger(__file__)
params = st.experimental_get_query_params()
st.session_state.auth_token = params.get("auth_token", [None])[0]
auth_token = st.session_state.auth_token

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
        utils.navigate_to(
          f"{APP_BASE_PATH}/Chat?agent_name={agent_name}"
          f"&auth_token={auth_token}")

  with start_query:
    # Get all query engines as a list
    query_engine_list = get_all_query_engines(auth_token=auth_token)

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
        if query_button:
          utils.navigate_to(
            f"{APP_BASE_PATH}/Query?query_engine_id={query_engine_id}"
            f"&auth_token={auth_token}")

  with build_query:
    with st.container():
      "Managing Query Engines"
      build_button = st.button("Start", key=4)
      if build_button:
        utils.navigate_to(
          f"{APP_BASE_PATH}/Query_Engines?auth_token={auth_token}")


if __name__ == "__main__":
  utils.init_api_base_url()
  landing_page()
