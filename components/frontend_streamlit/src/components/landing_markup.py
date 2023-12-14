import streamlit as st

def landing_theme():
  LANDING_STYLES = """
    <style>
      body, div, span, h1, h2, h3, button {
        font-family: Arial;
      }
      .main .stHeadingContainer h1 {
        color: #1F1F1F;
      }
      .main .stHeadingContainer h3 {
        font-size: 1.375rem;
        font-weight: normal;
        color: rgb(0 0 0 / 64%);
      }
      .stButton[data-testid="stFormSubmitButton"] {
        display: none;
      }
      [data-testid="stSidebarNavItems"] {
        padding-top: 1rem;
      }
      .stTextInput input {
        color: #555555;
        -webkit-text-fill-color: black;
        padding-top: 0.9rem;
        padding-bottom: 0.9rem;
        padding-left: 0.85rem;
        padding-right: 0.85rem;
      }
    </style>
  """
  st.markdown(LANDING_STYLES, unsafe_allow_html=True)
  