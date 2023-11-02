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
from common.models import Agent, UserChat
from api import get_all_chats, get_chat, run_agent

# For development purpose:
params = st.experimental_get_query_params()
if "auth_token" not in st.session_state:
  st.session_state.auth_token = params.get("auth_token", [None])[0]
st.session_state.chat_id = params.get("chat_id", [None])[0]
st.session_state.agent_name = params.get("MediKate", ["Chat"])[0]
assert st.session_state.auth_token, "The query parameter 'auth_token' is not set."

# Retrieve chat history.
st.session_state.user_chats = get_all_chats(
    auth_token=st.session_state.auth_token)


def on_input_change():
  user_input = st.session_state.user_input
  # Appending messages.
  st.session_state.messages.append({"HumanInput": user_input})

  # Send API to llm-service
  response = run_agent(agent_name, user_input, chat_id=st.session_state.chat_id)
  st.session_state.chat_id = response["chat"]["id"]
  st.session_state.messages.append({"AIOutput": response["content"]})

  # Clean up input field.
  st.session_state.user_input = ""


def chat_list_panel():
  with st.sidebar:
    st.header("My Chats")
    for user_chat in (st.session_state.user_chats or []):
      agent_name = user_chat["agent_name"]
      chat_id = user_chat["id"]
      with st.container():
        st.link_button(
            f"{agent_name} (id: {chat_id})",
            f"/Chat?chat_id={chat_id}&auth_token={st.session_state.auth_token}",
            use_container_width=True)


def right_panel():
  st.header("Plan")
  items = ["Item 1", "Item 2", "Item 3"]
  for item in items:
    st.write(item)


def init_messages():
  messages = []
  if st.session_state.chat_id:
    chat_data = get_chat(st.session_state.chat_id)
    messages = chat_data.get("history", [])
  else:
    messages.append({"AIOutput": "You can ask me anything."})
  # Initialize with chat history if any.
  st.session_state.setdefault("messages", messages)


def chat_content():
  init_messages()

  # Create a placeholder for all chat history.
  chat_placeholder = st.empty()
  with chat_placeholder.container():
    index = 1
    for item in st.session_state.messages:
      if "HumanInput" in item:
        message(item["HumanInput"], is_user=True, key=f"human_{index}")

      if "AIOutput" in item:
        message(
            item["AIOutput"],
            key=f"ai_{index}",
            allow_html=False,
            is_table=False,  # TODO: Detect whether an output content type.
        )
      index = index + 1

  st.text_input("User Input:", on_change=on_input_change, key="user_input")


def chat_page():
  st.title(st.session_state.agent_name)

  # List all existing chats if any. (data model: UserChat)
  chat_list_panel()

  # Set up columns to mimic a right-side sidebar
  main_container = st.container()
  with main_container:
    main_area, right_sidebar = st.columns([9, 3], gap="large")

    with main_area:
      # Render chat messages.
      chat_content()

    with right_sidebar:
      right_panel()


if __name__ == "__main__":
  chat_page()
