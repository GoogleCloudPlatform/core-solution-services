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
  Streamlit app Query Page
"""
# pylint: disable=invalid-name
import streamlit as st
from api import get_chat, run_query
from components.chat_history import chat_history_panel
import utils

# For development purpose:
params = st.experimental_get_query_params()
st.session_state.auth_token = params.get("auth_token", [None])[0]
st.session_state.chat_id = params.get("chat_id", [None])[0]
st.session_state.query_engine_id = params.get("query_engine_id", [None])[0]


def on_input_change():
  user_input = st.session_state.user_input
  query_engine_id = st.session_state.query_engine_id
  # Appending messages.
  st.session_state.messages.append({"HumanInput": user_input})

  # Send API to llm-service
  response = run_query(query_engine_id, user_input,
                       chat_id=st.session_state.chat_id)

  query_result = response["query_result"]
  query_references = response.get("query_references", None)

  st.session_state.messages.append({"AIOutput": query_result["response"]})

  if query_references:
    st.session_state.messages.append({"References": query_references})

  # Clean up input field.
  st.session_state.user_input = ""


def init_messages():
  messages = []
  if st.session_state.chat_id:
    chat_data = get_chat(st.session_state.chat_id)
    messages = chat_data.history
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
        with st.chat_message("user"):
          st.write(item["HumanInput"], is_user=True, key=f"human_{index}")

      if "AIOutput" in item:
        with st.chat_message("ai"):
          st.write(
              item["AIOutput"],
              key=f"ai_{index}",
              allow_html=False,
              is_table=False,  # TODO: Detect whether an output content type.
          )

      if "References" in item:
        with st.chat_message("ai"):
          for reference in item["References"]:
            document_url = reference["document_url"]
            document_text = reference["document_text"]
            st.text_area(f"Reference: {document_url}", document_text)
          st.divider()

  st.text_input("User Input:", on_change=on_input_change, key="user_input")


def chat_page():
  st.title("Query")
  st.write(f"Engine: {st.session_state.query_engine_id}")

  # List all existing chats if any. (data model: UserChat)
  chat_history_panel()

  # Set up columns to mimic a right-side sidebar
  main_container = st.container()
  with main_container:
    chat_content()


if __name__ == "__main__":
  utils.init_api_base_url()
  chat_page()
