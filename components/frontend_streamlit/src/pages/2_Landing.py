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
from streamlit.components.v1 import html
import importlib
utils = importlib.import_module("utils")

def landing_page():

  start_chat, col2, start_query = st.columns((1,1,1))


  with start_chat:
    with st.container():
        "Start a Chat with"
        st.selectbox(
            'Select an agent',
            ('MediKate', 'Casey'))
        chat_button=st.button("Start",key=2)
        if chat_button:
           utils.navigate_to("/Chat")


  with start_query:
    with st.container():
        "Start a Query with"
        query = st.selectbox(
            'Select a Query Engine',
            ('Query Engine 1', 'Query Engine 2'))
        query_button=st.button("Start",key=3)
        if query_button:
           utils.navigate_to("/Query")

if __name__ == "__main__":
  landing_page()
