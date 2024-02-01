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
Main page top content, includes logo img and select boxes
"""

from api import get_all_routing_agents
from components.chat_model_select import chat_model_select
from pathlib import Path
import streamlit as st
import validators
import base64
import os

top_content_styles = """
  <style>
    .main [data-testid="stImage"] {
      padding-top: 16px;
    }
    @media screen and (max-width: 1024px) {
      .main [data-testid="stImage"] img {
        max-width: 85% !important;
      }
    }
    @media screen and (min-width: 1024px) and (max-width: 1366px) {
      .main [data-testid="stImage"] img {
        max-width: 89% !important;
      }
    }
  </style>
"""

# Helper to read image from relative path
def add_logo(logo_path):
  logo_url = os.path.join(os.path.dirname(__file__), logo_path)
  if validators.url(logo_url) is True:
    logo = f"{logo_url}"
  else:
    logo = f"data:image/png;base64,"\
        f"{base64.b64encode(Path(logo_url).read_bytes()).decode()}"
  st.image(logo)


# Includes the logo and selection boxes for chat model
def landing_header():
  st.markdown(top_content_styles, unsafe_allow_html=True)

  routing_agents = get_all_routing_agents()
  routing_agent_names = list(routing_agents.keys())

  img, chat_mode = st.columns([6, 1.7])
  with img:
    add_logo("../assets/rit_logo.png")

  with chat_mode:
    chat_modes = routing_agent_names + ["Chat", "Plan", "Query"]
    selected_chat = st.selectbox(
        "Chat Mode", chat_modes)
    st.session_state.default_route = selected_chat

  st.session_state.default_route = selected_chat

  return {"chat_mode": selected_chat}


# Includes the logo and selection boxes for LLM type and chat model
def chat_header(refresh_func=None):
  st.markdown(top_content_styles, unsafe_allow_html=True)

  routing_agents = get_all_routing_agents()
  routing_agent_names = list(routing_agents.keys())

  img, model, chat_mode, refresh_button = st.columns([5, 3, 3, 2])
  with img:
    add_logo("../assets/rit_logo.png")
  with model:
    chat_model_select()
  with refresh_button:
    if refresh_func:
      st.button("Refresh", on_click=refresh_func)

  chat_modes = routing_agent_names + ["Chat", "Plan", "Query"]
  chat_mode_index = 0
  if st.session_state.default_route:
    while chat_mode_index < len(chat_modes):
      if st.session_state.default_route == chat_modes[chat_mode_index]:
        break
      chat_mode_index += 1
    if chat_mode_index >= len(chat_modes):
      chat_mode_index = 0

  with chat_mode:
    selected_chat = st.selectbox(
        "Chat Mode", chat_modes, index=chat_mode_index)
    st.session_state.default_route = selected_chat
