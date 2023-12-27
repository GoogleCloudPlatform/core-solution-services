import streamlit as st
from components.task_picker import task_picker_display
from styles.suggestions_markup import suggestions_component

"""
Center content for landing page
"""
def landing_suggestions():
  suggestions_component()

  info, plan, chat, query = st.columns(4)

  with info:
    with st.expander(f"Specify Task"):
      task_picker_display()

  with plan:
    with st.expander("Plan"):
      st.text("Generates and execute a plan to your specification")

  with chat:
    with st.expander("Chat"):
      st.text("Get answers with a standard prompt")

  with query:
    with st.expander("Query"):
      st.text("Utilize a data source to get answers")
