import streamlit as st

def suggestions_component():
  SUGGESTIONS_STYLES = """
    <style>
      [data-testid="stHorizontalBlock"]:has([data-testid="stExpander"]) > [data-testid="column"]:nth-child(4) {
        display: none;
      }
      [data-testid="stHorizontalBlock"]:has([data-testid="stExpander"]) > [data-testid="column"]:nth-child(4) summary:focus {
        
      }
    </style>
  """
  st.markdown(SUGGESTIONS_STYLES, unsafe_allow_html=True)
  