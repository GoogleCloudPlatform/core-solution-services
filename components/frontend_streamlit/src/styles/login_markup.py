import streamlit as st
from styles.style import colors

def login_theme():
  LOGIN_STYLES = f"""
    <style>
      body, div, span, h1, h2, h3, p, button, input {{
        font-family: Arial;
      }}
      [data-testid="textInputRootElement"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
      }}
      [data-testid="textInputRootElement"] {{
        background-color: {colors['light_fill']};
        border: 1px solid {colors['border_primary']};
        transition: border-color 0.1s ease-in, border-width 0.08s ease-in;
      }}
      [data-testid="textInputRootElement"]:has(input:focus) {{
        border: 2px solid {colors['tint_primary']};
      }}
      [data-testid="textInputRootElement"] input {{
        font-size: 15px;
        color: {colors['input_text']};
        padding: 0.58rem;
      }}

      .main .stHeadingContainer h1 {{
        font-size: 1.45rem;
        font-weight: 600;
        color: {colors['dim_text']};
      }}

      /* Main container styles */
      .main {{
        margin-top: 100px;
      }}
      .main [data-testid="block-container"] {{
        padding: 40px 24px;
        max-width: 40rem;
      }}

      /* Hidden elements */
      [data-testid="stDecoration"],
      [data-testid="stHeader"] {{
        display: none;
      }}

      /* Styles for submit button */
      [data-testid=stForm] .stButton button {{
        background-color: {colors['tint_primary']};
        color: {colors['light_fill']};
        border: 0;
        transition: background-color 0.1s ease-in;

        &:hover {{
          background-color: {colors['btn_hover']};
        }}
      }}
      [data-testid=stForm] .stButton {{
        padding-bottom: 20px;
        padding-top: 8px;
      }}
      [data-testid=stForm] .stButton button p {{
        font-size: 14px;
      }}
      [data-testid=stForm] .stButton button:focus:not(:active) {{
        color: {colors['light_fill']};
      }}

      .stAlert p {{
        font-size: 15px;
      }}
    </style>
  """
  st.markdown(LOGIN_STYLES, unsafe_allow_html=True)