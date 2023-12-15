import streamlit as st
from components.task_picker import task_picker_display
from styles.suggestions_markup import suggestions_component

def landing_suggestions():
  info, plan, chat, query = st.columns(4)

  with info:
    with st.expander(f"Specific Agent or Task\nTest and debug"):
      st.text("Test and debug")
      task_picker_display()

  with plan:
    with st.expander("Plan"):
      st.text("Test and debug")

  with chat:
    with st.expander("Chat"):
      st.text("Test and debug")

  with query:
    with st.expander("Query"):
      st.text("Test and debug")
