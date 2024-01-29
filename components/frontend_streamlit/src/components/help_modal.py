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
Help expander content
"""

import streamlit as st

def handle_click():
  st.session_state.help_state = not st.session_state.help_state

def help_form():
  name_col, pref_col = st.columns(2)

  with name_col:
    st.text_input("Name")

  with pref_col:
    pref = st.selectbox(
        "Contact Preference", ["Email", "Call", "Text"])

  contact_col, issue_col = st.columns(2)

  with contact_col:
    if pref == "Email":
      st.text_input("Email")
    else:
      st.text_input("Phone Number")

  with issue_col:
    st.text_input("Detail Your Issue")

  st.button("Send", on_click=handle_click)

