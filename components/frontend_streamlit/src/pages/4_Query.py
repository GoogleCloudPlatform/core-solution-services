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
from components.query_engine_select import query_engine_select
from components.chat_model_select import chat_model_select
from os.path import splitext
import logging
import utils


def on_input_change():
  user_input = st.session_state.user_input
  query_engine_id = st.session_state.query_engine_id
  # Appending messages.
  st.session_state.messages.append({"HumanInput": user_input})

  # Send API to llm-service
  if query_engine_id is None:
    logging.error("Invalid Query Engine")
    st.write("Invalid Query Engine")
    return
  response = run_query(query_engine_id, user_input,
                       chat_id=st.session_state.chat_id,
                       llm_type=st.session_state.chat_llm_type)

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
    messages = chat_data["history"]
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
    query_index = 1
    for item in st.session_state.messages:
      if "HumanInput" in item:
        with st.chat_message("user"):
          st.write(item["HumanInput"], is_user=True, key=f"human_{index}")

      if "AIOutput" in item:
        with st.chat_message("ai"):
          st.write(
              item["AIOutput"],
              key=f"ai_{index}",
              unsafe_allow_html=False,
              is_table=False,  # TODO: Detect whether an output content type.
          )

      if "References" in item:
        with st.chat_message("ai"):
          for reference in item["References"]:
            modality = reference["modality"]
            chunk_url = reference["chunk_url"]
            chunk_type = ""
            if chunk_url:
              _, chunk_type = splitext(chunk_url)
              chunk_url = chunk_url.replace("gs://",
                  "https://storage.googleapis.com/", 1)
            document_url = reference["document_url"]
            page = reference["page"]
            if page:
              # References from multimodal query engines have page numbers
              reference_header = f"\nReference {query_index}: {document_url}, Page {page+1}"
            else:
              # References from text-only query engines do not have page numbers
              reference_header = f"\nReference {query_index}: {document_url}"
            if modality == "text":
              document_text = reference["document_text"]
              st.text_area(
                reference_header,
                document_text,
                key=f"ref_{query_index}")
            elif modality == "image" and chunk_type in [".pdf",
                 ".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
              # .tif/.tiff not available, all other file types are untested
              st.write(
                reference_header,
                key=f"ref_{query_index}")
              st.image(chunk_url)
            else:
              logging.error("Reference modality unknown")
              st.write("Reference modality unkown")
            query_index = query_index + 1
          st.divider()

  st.text_input("User Input:", on_change=on_input_change, key="user_input")


def chat_page():
  st.title("Query")

  # List all existing chats if any. (data model: UserChat)
  chat_history_panel()

  # Set up columns to mimic a right-side sidebar
  main_container = st.container()
  with main_container:
    col1, col2 = st.columns([3, 3])
    with col1:
      query_engine_select()
    with col2:
      chat_model_select()
    chat_content()


if __name__ == "__main__":
  utils.init_page()
  chat_page()
