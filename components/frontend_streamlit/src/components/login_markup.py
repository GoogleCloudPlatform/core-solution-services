import streamlit as st

def login_theme():
  LOGIN_STYLES = """
    <style>
      [data-testid="textInputRootElement"] > div:nth-child(1) {
        background-color: #FFFFFF;
      }
      [data-testid="textInputRootElement"] {
        background-color: #FFFFFF;
        border: 1px solid #686868;
        transition: border-color 0.1s ease-in, border-width 0.1s ease-in;
      }
      [data-testid="textInputRootElement"]:has(input:focus) {
        border: 2px solid #4285f4;
        border-radius: .5rem;
      }
      [data-testid="stApp"] {
        background-color: #f4f6fc;
      }
    </style>
  """
  st.markdown(LOGIN_STYLES, unsafe_allow_html=True)