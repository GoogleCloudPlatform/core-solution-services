import streamlit as st

def landing_theme():
  LANDING_STYLES = """
    <style>
      body, div, span, h1, h2, h3, button {
        font-family: Arial;
      }
      .main .stHeadingContainer h1 {
        color: #1F1F1F;
        padding-bottom: 1.6rem;
        padding-top: 1.6rem;
        padding-bottom: 1.6rem;
      }
      .main .stHeadingContainer h3 {
        font-size: 1.375rem;
        font-weight: normal;
        color: rgb(0 0 0 / 64%);
        padding-bottom: 2.7rem;
      }
      .stButton[data-testid="stFormSubmitButton"] {
        display: none;
      }
      [data-testid="stSidebarNavItems"] {
        padding-top: 1rem;
      }
      .main [data-testid="block-container"],
      .main [data-testid="stVerticalBlockBorderWrapper"],
      .main [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1),
      .main [data-testid="stForm"] {
        height: 100%;
      }
      [data-testid="stTextInput"] {
        align-self: flex-end;
      }
      .main [data-testid="element-container"]:has([data-testid="stTextInput"]) {
        display: flex;
        flex: 1;
      }
      .main [data-testid="stVerticalBlock"]:has([data-testid="stTextInput"]) {
        gap: 0;
      }
      [data-testid="textInputRootElement"] > div:nth-child(1) {
        background-color: #FFFFFF;
      }
      [data-testid="textInputRootElement"] {
        background-color: #FFFFFF;
        border: 1px solid #80868b;
        transition: border-color 0.1s ease-in, border-width 0.2s ease-in;
        border-radius: .88rem;
      }
      [data-testid="textInputRootElement"]:has(input:focus) {
        border: 2px solid #4285f4;
      }
      [data-testid="textInputRootElement"] input {
        font-family: Arial;
        color: #5f6368;
        -webkit-text-fill-color: black;
        padding-top: 0.9rem;
        padding-bottom: 0.9rem;
        padding-left: 0.85rem;
        padding-right: 0.85rem;
      }
    </style>
  """
  st.markdown(LANDING_STYLES, unsafe_allow_html=True)
  