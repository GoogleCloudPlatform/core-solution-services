import streamlit as st
from styles.style import colors
from styles.sidebar_logo import display_side_logo

def main_styles():
  display_side_logo()

  SHARED_STYLES = f"""
    <style>
      /* Global font family */
      body, div, span, h1, h2, h3, p, button, input {{
        font-family: Arial;
      }}

      /* Main container styles */
      .main {{
        background-color: {colors['background']};
        border-radius: 18px;
        margin-top: 64px;
        margin-bottom: 24px;
        margin-right: 56px;
      }}
      .main [data-testid="block-container"] {{
        padding: 40px 24px;
        max-width: 60rem;
      }}

      /* Sidebar panel color */
      [data-testid="stSidebar"] {{
        background-color: {colors['light_fill']};
      }}

      /* Hidden elements */
      [data-testid="stDecoration"],
      [data-testid="stHeader"] {{
        display: none;
      }}
    </style>
  """
  st.markdown(SHARED_STYLES, unsafe_allow_html=True)
