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
from components.chat_history import chat_history_panel
from components.landing_header import display_header
from components.suggestions import landing_suggestions
from styles.sidebar_logo import display_side_logo
from styles.landing_markup import landing_theme
from common.utils.logging_handler import Logger
import utils

Logger = Logger.get_logger(__file__)

def landing_page():
  landing_theme()
  display_side_logo()
  chat_history_panel()

  chat_selection = display_header()

  st.title("Hello again")
  st.subheader("Start your journey here or explore the options below.")

  landing_suggestions()

  with st.form("user_input_form", border=False, clear_on_submit=True):
    input_col, btn_col = st.columns([9.3, .7])

    with input_col:
      user_input = st.text_input(
        placeholder="Enter a prompt here",
        label="Enter prompt",
        label_visibility="collapsed",
        key="landing_input"
      )
    
    with btn_col:
      submitted = st.form_submit_button("Submit")

    if submitted:
      st.session_state.landing_user_input = user_input
      st.session_state.chat_id = None
      utils.navigate_to("Chat")

if __name__ == "__main__":
  utils.init_page()
  landing_page()