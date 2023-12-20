import streamlit as st

def main_page():
  MAIN_STYLES = """<style>
  /* Global font family */
  body, div, span, h1, h2, h3, button, p {
    font-family: Arial;
  }

  /* Main container styles */
  .main {
    background-color: #f4f6fc;
    border-radius: 15px;
    margin: 64px 35px 25px;
    height: 100%;
  }

  /* Heading styles */
  .main .stHeadingContainer h1 {
    color: #1F1F1F;
    padding: 1.6rem 0;
  }
  .main .stHeadingContainer h3 {
    font-size: 1.375rem;
    font-weight: normal;
    color: rgba(0, 0, 0, 0.64);
    padding-bottom: 2.7rem;
  }

  /* Sidebar styles */
  [data-testid="stSidebarNavItems"] {
    padding-top: 1rem;
  }
  [data-testid="stSidebar"] {
    background-color: #FFFFFF;
  }

  /* Hidden elements */
  [data-testid="stDecoration"], [data-testid="stHeader"],
  .main [data-testid="stFormSubmitButton"] button p {
    display: none;
  }

  /* Block and container styles */
  .main [data-testid="stVerticalBlock"]:has([data-testid="stTextInput"]),
  .main [data-testid="block-container"],
  .main [data-testid="stVerticalBlockBorderWrapper"],
  .main [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1),
  .main [data-testid="stForm"],
  .main [data-testid="element-container"]:has([data-testid="stTextInput"]),
  .main [data-testid="element-container"]:has([data-testid="stFormSubmitButton"]) {
    display: flex;
    flex: 1;
    gap: 0;
    padding-top: 1.7rem;
  }

  /* Text input styles */
  [data-testid="textInputRootElement"],
  [data-testid="textInputRootElement"] > div:nth-child(1),
  [data-testid="textInputRootElement"] input {
    background-color: #FFFFFF;
    color: #5f6368;
    border: 1px solid #90989f;
    border-radius: .88rem;
    padding: 0.85rem;
    -webkit-text-fill-color: black;
    transition: border-color 0.1s ease-in, border-width 0.2s ease-in;
  }
  [data-testid="textInputRootElement"]:has(input:focus) {
    border: 2px solid #4285f4;
  }

  /* Button styles */
  .stButton[data-testid="stFormSubmitButton"],
  .main [data-testid="stFormSubmitButton"] button {
    align-self: flex-end;
    border: none;
    color: rgba(0, 0, 0, 0.64);
    background-color: transparent;
    float: right;
    padding: 0 0 .35rem;
    transition: color 0.1s ease-in;
  }
  .main [data-testid="stFormSubmitButton"] button:hover,
  .main [data-testid="stFormSubmitButton"] button::after {
    color: #4285f4;
  }
  .main [data-testid="stFormSubmitButton"] button::after {
    content: "➤";
    font-size: 26px;
  }

  /* Select box styles */
  .main [data-baseweb=select] > div:nth-child(1),
  .main [data-testid=stSelectbox] svg {
    cursor: pointer;
    border-color: #90989f;
    background-color: #FFFFFF;
    border-radius: 0.7rem;
    color: #5f6368;
  }

  /* Dropdown list styles */
  [data-testid=stVirtualDropdown] li {
    background-color: #FFFFFF;
  }
  </style>"""
  st.markdown(MAIN_STYLES, unsafe_allow_html=True)
  