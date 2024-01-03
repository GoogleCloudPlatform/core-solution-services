import streamlit as st
from styles.style_constants import colors, decoration

def history_styles():
  HISTORY_STYLE = f"""<style>
  /* General styles for sidebar content */
  [data-testid=stSidebarUserContent] {{
    /* Button styles */
    .stButton button {{
      background-color: #c4eed0;
      color: {colors['text_primary']};
      font-weight: bold;
      text-align: left;
      border: 0;
      border-radius: {decoration['border_radius']};
      display: block !important;
      transition: background-color 0.1s ease-in;

      /* Hover state for buttons */
      &:hover {{
        background-color: #b9e2c5;
      }}

      &:focus:not(:active) {{
        color: {colors['text_primary']};
      }}
    }}

    /* Styles for horizontal block buttons - new chat and clear */
    [data-testid=stHorizontalBlock] .stButton button {{
      background-color: {colors['tint_primary']};
      color: {colors['light_fill']};
      float: right;

      &:hover {{
        background-color: {colors['btn_hover']};
      }}
    }}

    /* Styles for text in vertical block chat history buttons */
    [data-testid=stVerticalBlockBorderWrapper] .stButton p {{
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      font-family: Arial;
      font-size: .875rem;
    }}

    h3 {{
      padding-top: .52rem;
      font-weight: 500;
    }}
  }}

  /* Styles for the sidebar navigation separator */
  [data-testid=stSidebarNavSeparator] {{
    margin-left: 20px;
    margin-right: 20px;
  }}

  [data-testid="stSidebarNavItems"] {{
    padding-top: 1rem;
  }}
  </style>"""
  st.markdown(HISTORY_STYLE, unsafe_allow_html=True)
  