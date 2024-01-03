import streamlit as st
from styles.sidebar_logo import display_side_logo
from styles.style_constants import colors

def login_theme():
  display_side_logo()

  LOGIN_STYLES = f"""
    <style>
      /* Text input field styles */
      [data-testid="textInputRootElement"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
      }}
      [data-testid="textInputRootElement"] {{
        background-color: {colors['light_fill']};
        border: 1px solid {colors['border_primary']};
        transition: border-color 0.1s ease-in, border-width 0.25s ease-in;
      }}
      [data-testid="textInputRootElement"]:has(input:focus) {{
        border: 2px solid {colors['tint_primary']};
      }}
      [data-testid="textInputRootElement"] input {{
        color: {colors['input_text']};
        -webkit-text-fill-color: {colors['input_text']};
        padding: 0.58rem;
      }}
      [data-testid="InputInstructions"] {{
        display: none;
      }}

      .main .stHeadingContainer h1 {{
        font-family: Arial;
        font-weight: 600;
        color: {colors['dim_text']};
      }}

      /* Main container styles */
      .main {{
        margin-top: 3.5vh;
      }}
      .main [data-testid="block-container"] {{
        padding: 40px 24px;
        max-width: 36rem;
      }}

      /* Hidden elements */
      [data-testid="stDecoration"],
      [data-testid="stHeader"] {{
        display: none;
      }}

      /* Styles for submit button */
      [data-testid=stForm] .stButton {{
        padding-bottom: 20px;
        padding-top: 8px;
      }}
      [data-testid=stForm] .stButton button {{
        background-color: {colors['tint_primary']};
        color: {colors['light_fill']};
        border: none;
        transition: background-color 0.1s ease-in;

        &:hover {{
          background-color: {colors['btn_hover']};
        }}

        &:focus:not(:active) {{
          color: {colors['light_fill']};
        }}
      }}

      .stAlert p {{
        color: {colors['dim_text']};
      }}

      [data-testid="stSidebarNavItems"] {{
        padding-top: 1.1rem;
      }}

      /* Smartphones and small devices */
      @media screen and (max-width: 1024px) {{
        .main .stHeadingContainer h1 {{
          font-size: 18px;
        }}
        .main [data-testid="block-container"] {{
          max-width: 30rem;
        }}
      }}

      /* Laptops and small displays */
      @media screen and (min-width: 1024px) and (max-width: 1366px) {{
        .main .stHeadingContainer h1 {{
          font-size: 24px;
        }}
      }}

      /* Large monitors */
      @media screen and (min-width: 1366px) and (max-width: 1600px) {{
        .main .stHeadingContainer h1 {{
          font-size: 28px;
        }}
      }}

      /* Very large monitors */
      @media screen and (min-width: 1600px) {{
        .main .stHeadingContainer h1 {{
          font-size: 30px;
        }}
      }}
    </style>
  """
  st.markdown(LOGIN_STYLES, unsafe_allow_html=True)