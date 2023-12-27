import streamlit as st
from styles.style import colors

def suggestions_component():
  SUGGESTIONS_STYLES = f"""
    <style>
      .main [data-testid="stExpander"] details {{
        border-color: {colors['light_fill']};
        border-radius: 0.7rem;
        background-color: {colors['light_fill']};
        color: {colors['dim_text']};
      }}
      .main [data-testid="stExpander"] [data-testid="stText"] {{
        font-family: Arial;
        text-wrap: wrap;
      }}
      .main [data-testid="stExpander"] summary:hover {{
        color: #3b3a3a;
      }}
      .main [data-testid="stExpander"] summary svg {{
        display: none;
      }}
      .main [data-testid="stExpander"] summary p {{
        font-weight: 600;
        font-size: 16px;
      }}
    </style>
  """
  st.markdown(SUGGESTIONS_STYLES, unsafe_allow_html=True)
  