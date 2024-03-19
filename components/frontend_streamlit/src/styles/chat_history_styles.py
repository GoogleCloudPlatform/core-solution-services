# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Contains the styles for the sidebar content and chat history
"""

import streamlit as st
from styles.style_constants import colors, decoration

def history_styles():
  chat_history_style = f"""<style>
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

      &:focus:not(:active) {{
        color: {colors['light_fill']};
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
      color: {colors['text_primary']};
    }}
  }}

  @media (prefers-color-scheme: dark) {{
    [data-testid=stSidebarNavLink] span {{
      color: {colors['text_primary']};
    }}
  }}

  /* Styles for the sidebar navigation separator */
  [data-testid=stSidebarNavSeparator] {{
    margin-left: 20px;
    margin-right: 20px;
    border-bottom-color: rgb(49 51 63 / 60%);
  }}

  [data-testid="stSidebarNavItems"] {{
    padding-top: 1rem;
  }}
  </style>"""
  st.markdown(chat_history_style, unsafe_allow_html=True)
  