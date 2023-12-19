import streamlit as st

def display_side_logo():
  NAV_STYLES = """
    <style>
      [data-testid="stSidebarNav"]::before {
        content: "GENIE";
        font-size: 26px;
        font-weight: 500;
        color: #5f6368;
        padding-left: 60px;
        font-family: Arial;
      }
      [data-testid="stSidebarNav"] {
        padding-top: 18.5px;
      }
      [data-testid="stSidebarContent"] [data-testid="baseButton-header"]::after {
        content: "≡";
        font-size: 35px;
        color: #5f6368;
      }
      [data-testid="stSidebarContent"] [data-testid="baseButton-header"] svg {
        display: none;
      }
      [data-testid="stSidebarContent"] div:has([data-testid="baseButton-header"]) {
        width: 22px;
        top: 0.8rem;
        right: 0;
        left: 0.85rem;
      }
    </style>
  """
  st.markdown(NAV_STYLES, unsafe_allow_html=True)