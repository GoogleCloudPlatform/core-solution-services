import streamlit as st
from styles.style import colors
from styles.shared_styles import main_styles

def landing_theme():
  main_styles()

  LANDING_STYLES = f"""
    <style>
      /* Hidden elements */
      .main [data-testid="stFormSubmitButton"] button p {{
        display: none;
      }}

      /* Heading styles */
      .main .stHeadingContainer h1 {{
        color: {colors['text_primary']};
        padding-bottom: 1.6rem;
        padding-top: 1.6rem;
        padding-bottom: 1.6rem;
      }}
      .main .stHeadingContainer h3 {{
        font-size: 1.375rem;
        font-weight: normal;
        color: {colors['dim_text']};
        padding-bottom: 2.7rem;
      }}
      .main [data-testid="stVerticalBlock"]:has([data-testid="stTextInput"]) {{
        gap: 0;
      }}
      
      /* Text input positioning */
      .main [data-testid="block-container"],
      .main [data-testid="stVerticalBlockBorderWrapper"],
      .main [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1),
      .main [data-testid="stForm"] {{
        height: 100%;
      }}
      [data-testid="stTextInput"],
      .stButton[data-testid="stFormSubmitButton"] {{
        align-self: flex-end;
      }}
      .main [data-testid="element-container"]:has([data-testid="stTextInput"]),
      .main [data-testid="element-container"]:has([data-testid="stFormSubmitButton"]) {{
        display: flex;
        flex: 1;
      }}

      /* Text input styling */
      [data-testid="textInputRootElement"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
      }}
      [data-testid="textInputRootElement"] {{
        background-color: {colors['light_fill']};
        border: 1px solid {colors['border_primary']};
        transition: border-color 0.1s ease-in, border-width 0.08s ease-in;
        border-radius: 18px;
      }}
      [data-testid="textInputRootElement"]:has(input:focus) {{
        border: 2px solid {colors['tint_primary']};
      }}
      [data-testid="textInputRootElement"] input {{
        color: {colors['input_text']};
        -webkit-text-fill-color: {colors['input_text']};
        padding: 0.85rem;
      }}
      .main [data-testid="stFormSubmitButton"] button {{
        border: none;
        padding-bottom: .35rem;
        padding-left: 0;
        float: right;
        color: {colors['dim_text']};
        background-color: transparent;
      }}
      .main [data-testid="stFormSubmitButton"] button:hover {{
        color: {colors['tint_primary']};
      }}
      .main [data-testid="stFormSubmitButton"] button::after {{
        content: "➤";
        font-size: 26px;
        transition: color 0.1s ease-in;
      }}

      /* Select input box styling */
      .main [data-baseweb=select] > div:nth-child(1) {{
        cursor: pointer;
        border-color: {colors['border_primary']};
        background-color: {colors['light_fill']};
        border-radius: 0.7rem;
      }}
      .main [data-testid=stSelectbox] svg {{
        color: {colors['input_text']};
      }}
      [data-testid=stVirtualDropdown] li {{
        background-color: {colors['light_fill']};
      }}
    </style>
  """
  st.markdown(LANDING_STYLES, unsafe_allow_html=True)
