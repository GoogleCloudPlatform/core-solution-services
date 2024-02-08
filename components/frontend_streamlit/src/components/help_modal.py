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
import time

def handle_click(messages_cont, spinner_cont, help_cont, input_cont):
  # Clear original message
  with help_cont:
    st.write("")

  start_time = time.time()
  count = 0
  time_elapsed = 0

  while time_elapsed < 4:
    count += 1
    with spinner_cont:
      with st.chat_message("ai"):
        st.write("Loading." + "." * int(count % 3),
                 is_user=True, key="help_loading2")

      time.sleep(1)
      time_elapsed = time.time() - start_time

  # Clear initial human output message
  with input_cont:
    st.write("")
  # Hide spinner
  with spinner_cont:
    st.write("")

  with messages_cont:
    with st.chat_message("ai"):
      st.markdown(
        "Your ticket number is: **5010**<br>"\
        "You will receive an **email notification** "\
        "within 48 hours.<br>"\
        "You may continue to utilize the chat assistant, "\
        "or can close or navigate away from this window.",
        unsafe_allow_html=True
      )

def help_form(messages_cont, spinner_cont, help_cont, input_cont):
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

  st.button("Send", on_click=handle_click,
            args=[messages_cont, spinner_cont, help_cont, input_cont])

