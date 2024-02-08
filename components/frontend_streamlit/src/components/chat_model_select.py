# Copyright 2024 Google LLC
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
Model select component
"""

import streamlit as st
from api import get_all_chat_llm_types
import logging


def chat_model_select():
  chat_llm_types = get_all_chat_llm_types(
    auth_token=st.session_state.auth_token)

  chat_llm_types = ["default"] + chat_llm_types

  with st.container():
    try:
      selected_model_index = chat_llm_types.index(
          st.session_state.get("chat_llm_type"))
    except ValueError:
      selected_model_index = 0
    selected_model = st.selectbox(
        "Model", chat_llm_types, index=selected_model_index)
    st.session_state.chat_llm_type = selected_model
    logging.info(f"setting chat_llm_type to {selected_model}")
