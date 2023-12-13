import streamlit as st

def display_logo():
  NAV_STYLES = """
    <style>
      [data-testid="stSidebarNav"]::before {
        content: "GENIE";
        font-size: 26px;
        color: #606060;
        padding-left: 60px;
        font-family: Arial;
      }
      [data-testid="stSidebarNav"] {
        padding-top: 18.5px;
      }
      [data-testid="stSidebarContent"] button:has(svg)::after {
        content: "≡";
        font-size: 35px;
        color: #606060;
      }
      [data-testid="stSidebarContent"] svg {
        display: none;
      }
      [data-testid="stSidebarContent"] div:has(svg) {
        width: 22px;
        top: 0.8rem;
        right: 0;
        left: 0.85rem;
      }
    </style>
  """
  st.markdown(NAV_STYLES, unsafe_allow_html=True)