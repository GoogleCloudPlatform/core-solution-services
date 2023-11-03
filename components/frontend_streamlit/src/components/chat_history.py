import streamlit as st
from api import get_all_chats


def chat_history_panel():
  # Retrieve chat history.
  st.session_state.user_chats = get_all_chats(
      auth_token=st.session_state.auth_token)

  with st.sidebar:
    st.header("My Chats")
    for user_chat in (st.session_state.user_chats or []):
      chat_id = user_chat["id"]

      if "agent_name" in user_chat:
        agent_name = user_chat["agent_name"]

      with st.container():
        st.link_button(
            f"{agent_name} (id: {chat_id})",
            f"/Chat?chat_id={chat_id}&auth_token={st.session_state.auth_token}",
            use_container_width=True)
