import streamlit as st
from components.main_logo import add_logo

def display_header():
  TOP_STYLES = """
    <style>
      .main [data-testid="stImage"] {
        padding-top: 16px;
      }
    </style>
  """
  st.markdown(TOP_STYLES, unsafe_allow_html=True)

  img, chat_mode = st.columns([8.2, 1.8])
  with img:
    add_logo('../assets/rit_logo.png')
  with chat_mode:
    selected_chat = st.selectbox(
        "Chat Mode", ["Auto", "Chat", "Plan", "Query"])
    st.session_state.default_route = selected_chat
    return selected_chat