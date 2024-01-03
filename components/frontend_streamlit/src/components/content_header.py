from pathlib import Path
from api import get_all_chat_llm_types
import streamlit as st
import validators
import base64
import os

"""
Helper to read image from relative path
"""
def add_logo(logo_path: str):
  logo_url = os.path.join(os.path.dirname(__file__), logo_path)

  if validators.url(logo_url) is True:
    logo = f"{logo_url}"
  else:
    logo = f"data:image/png;base64,{base64.b64encode(Path(logo_url).read_bytes()).decode()}"
  st.image(logo)

"""
Includes the logo and selection boxes for LLM type and chat mode
"""
def display_header():
  TOP_STYLES = """
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
          max-width: 90% !important;
        }
      }
    </style>
  """
  st.markdown(TOP_STYLES, unsafe_allow_html=True)

  chat_llm_types = get_all_chat_llm_types()

  img, model, chat_mode = st.columns([6, 1.7, 1.7])
  with img:
    add_logo('../assets/rit_logo.png')
  
  with model:
    selected_model = st.selectbox(
        "Model", chat_llm_types)
    st.session_state.chat_llm_type = selected_model

  with chat_mode:
    selected_chat = st.selectbox(
        "Chat Mode", ["Auto", "Chat", "Plan", "Query"])
    st.session_state.default_route = selected_chat

  return {"model": selected_model, "chat_mode": selected_chat}