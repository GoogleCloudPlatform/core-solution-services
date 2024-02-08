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
from components.content_header import landing_header
from components.suggestions import landing_suggestions
from styles.pages.landing_markup import landing_theme
import utils


def landing_page():
  """
  Landing Page
  """
  chat_history_panel()

  # Clean up session.
  utils.reset_session_state()

  landing_theme()

  # Returns the values of the select input boxes
  selections = landing_header()

  st.title("Welcome")
  st.subheader("Start your journey here or explore the options below.")

  # Center content
  landing_suggestions()

  with st.form("user_input_form", border=False, clear_on_submit=True):
    input_col, btn_col = st.columns([9.4, .6])

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
      utils.reset_session_state()
      st.session_state.landing_user_input = user_input
      utils.navigate_to("Chat")

if __name__ == "__main__":
  utils.init_page()
  landing_page()
