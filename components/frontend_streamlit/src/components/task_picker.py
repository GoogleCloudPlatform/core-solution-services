import streamlit as st
from common.utils.logging_handler import Logger
from api import get_all_query_engines
import utils

def task_picker_display():
  st.subheader("Run with a specific Agent or Task:")
  start_chat, start_query = st.columns((1, 1))

  with start_chat:
    with st.container():
      agent_name = st.selectbox(
          "Agent:",
          ("Chat", "Plan"))
      chat_button = st.button("Start", key=2)
      if chat_button:
        st.session_state.agent_name = agent_name
        st.session_state.chat_id = None
        utils.navigate_to("Agent")

  with start_query:
    # Get all query engines as a list
    query_engine_list = get_all_query_engines(
      auth_token=st.session_state.auth_token)

    if query_engine_list is None or len(query_engine_list) == 0:
      with st.container():
        "No Query Engines"
    else:
      query_engines = {}
      for item in query_engine_list:
        query_engines[item["name"]] = item

      Logger.info(query_engines)
      with st.container():
        qe_name = st.selectbox(
            "Query Engine:",
            tuple(query_engines.keys()))
        query_button = st.button("Start", key=3)
        query_engine_id = query_engines[qe_name]["id"]
        st.session_state.query_engine_id = query_engine_id
        if query_button:
          st.session_state.agent_name = agent_name
          st.session_state.chat_id = None
          utils.navigate_to("Query")