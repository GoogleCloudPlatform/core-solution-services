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

import streamlit as st
import utils

params = st.experimental_get_query_params()
auth_token = params.get("auth_token")[0]

def landing_page():
  st.title("Welcome.")

  start_chat, col2, start_query = st.columns((1,1,1))

  with start_chat:
    with st.container():
      "Start a Chat with"
      agent_name = st.selectbox(
          'Select an agent',
          ('MediKate', 'Casey'))
      chat_button=st.button("Start",key=2)
      if chat_button:
        utils.navigate_to(f"/Chat?agent_name={agent_name}&auth_token={auth_token}")

  with start_query:
    with st.container():
      "Start a Query with"
      query_engine = st.selectbox(
          'Select a Query Engine',
          ('qe1', 'qe2'))
      query_button=st.button("Start",key=3)
      if query_button:
          utils.navigate_to(f"/Query?query_engine={query_engine}&auth_token={auth_token}")

if __name__ == "__main__":
  utils.init_api_base_url()
  landing_page()
