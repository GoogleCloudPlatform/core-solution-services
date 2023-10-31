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
from streamlit_chat import message
from streamlit.components.v1 import html


def on_input_change():
  user_input = st.session_state.user_input
  st.session_state.past.append(user_input)
  st.session_state.generated.append({
      "type": "normal",
      "data": f"Generated message from {user_input}"
  })

def on_btn_click():
  del st.session_state.past[:]
  del st.session_state.generated[:]

def chat_page():
  st.title("Casey")

  # Set up columns to mimic a right-side sidebar
  main_area, right_sidebar = st.columns([8, 3], gap="large")

  with main_area:
    st.session_state.setdefault("past", ["Hello"])
    st.session_state.setdefault("generated", [{
        "type": "normal",
        "data": "Line 1 \n Line 2 \n Line 3"
    }])
    st.button("Clear message", on_click=on_btn_click, key=1000)

    # Create a placeholder for all chat history.
    chat_placeholder = st.empty()
    with chat_placeholder.container():
      for i in range(len(st.session_state["generated"])):
        # Add user's message.
        message(st.session_state["past"][i], is_user=True, key=f"{i}_user")
        # Add AI-generated message.
        message(
            st.session_state["generated"][i]["data"],
            key=f"{i}",
            allow_html=False,
            is_table=True
            if st.session_state["generated"][i]["type"] == "table" else False
        )

    st.text_input("User Input:", on_change=on_input_change, key="user_input")

  with right_sidebar:
    st.header("Plan")
    items = ["Item 1", "Item 2", "Item 3"]
    for item in items:
      st.write(item)

if __name__ == "__main__":
  chat_page()
