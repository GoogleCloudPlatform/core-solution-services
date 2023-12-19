import streamlit as st

def landing_theme():
  LANDING_STYLES = """
    <style>
      body, div, span, h1, h2, h3, button, p {
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
      [data-testid="stSidebarNavItems"] {
        padding-top: 1rem;
      }
      [data-testid="stDecoration"],
      [data-testid="stHeader"],
      .main [data-testid="stFormSubmitButton"] button p {
        display: none;
      }
      .main {
        background-color: #f4f6fc;
        border-radius: 15px;
        margin-top: 64px;
        margin-bottom: 25px;
        margin-right: 35px;
      }
      [data-testid="stSidebar"] {
        background-color: #FFFFFF;
      }
      .main [data-testid="stVerticalBlock"]:has([data-testid="stTextInput"]) {
        gap: 0;
      }
      .main [data-testid="block-container"] {
        padding-top: 1.7rem;
      }
      .main [data-testid="block-container"],
      .main [data-testid="stVerticalBlockBorderWrapper"],
      .main [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1),
      .main [data-testid="stForm"] {
        height: 100%;
      }
      [data-testid="stTextInput"],
      .stButton[data-testid="stFormSubmitButton"] {
        align-self: flex-end;
      }
      .main [data-testid="element-container"]:has([data-testid="stTextInput"]),
      .main [data-testid="element-container"]:has([data-testid="stFormSubmitButton"]) {
        display: flex;
        flex: 1;
      }
      [data-testid="textInputRootElement"] > div:nth-child(1) {
        background-color: #FFFFFF;
      }
      [data-testid="textInputRootElement"] {
        background-color: #FFFFFF;
        border: 1px solid #90989f;
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
        padding: 0.85rem;
      }
      .main [data-testid="stFormSubmitButton"] button {
        border: none;
        padding-bottom: .35rem;
        padding-left: 0;
        float: right;
        color: rgb(0 0 0 / 64%);
        background-color: transparent;
      }
      .main [data-testid="stFormSubmitButton"] button:hover {
        color: #4285f4;
      }
      .main [data-testid="stFormSubmitButton"] button::after {
        content: "➤";
        font-size: 26px;
        transition: color 0.1s ease-in;
      }
      .main [data-baseweb=select] > div:nth-child(1) {
        cursor: pointer;
        border-color: #90989f;
        background-color: #FFFFFF;
        border-radius: 0.7rem;
      }
      .main [data-testid=stSelectbox] svg {
        color: #5f6368;
      }
      [data-testid=stVirtualDropdown] li {
        background-color: #FFFFFF;
      }
    </style>
  """
  st.markdown(LANDING_STYLES, unsafe_allow_html=True)
  