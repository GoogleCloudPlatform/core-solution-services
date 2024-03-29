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
Common and generic styles used throughout various main pages
"""

import streamlit as st
from styles.style_constants import colors

def main_styles():

  shared_styles = f"""
    <style>
      /* Main container styles */
      .main {{
        border-radius: 12px;
        margin-top: 12px;
        margin-bottom: 12px;
        margin-left: 12px;
      }}
      .main .block-container {{
        padding-top: 0;
        padding-bottom: 0;
      }}

      /* Hidden elements */
      [data-testid="stDecoration"],
      [data-testid="stHeader"] {{
        display: none;
      }}
      [data-testid="InputInstructions"] {{
        display: none;
      }}

      /* Generic button styles */
      .main .stButton [data-testid="baseButton-secondary"] {{
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

      /* Select input box styling */
      [data-baseweb=select] > div:nth-child(1) {{
        cursor: pointer;
        border-color: {colors['border_primary']};
        background-color: {colors['light_fill']};
        color: {colors['text_primary']};
      }}
      [data-testid=stSelectbox] label p {{
        color: {colors['text_primary']};
        font-size: 15px;
      }}
      [data-testid=stSelectbox] svg {{
        color: #5f6368;
      }}
      [data-testid=stVirtualDropdown] li {{
        background-color: {colors['light_fill']};
        color: {colors['text_primary']};
      }}
      [data-testid=stVirtualDropdown] {{
        background-color: {colors['light_fill']};
      }}
      [data-testid=stVirtualDropdown] li:hover {{
        background-color: rgb(240, 242, 246);
      }}
      [data-baseweb="tooltip"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
        color: {colors['text_primary']};
      }}

      a {{
        color: {colors['tint_primary']} !important;
      }}
      strong, ul, li {{
        color: {colors['text_primary']};
      }}

      /* Smartphones and small devices */
      @media screen and (max-width: 1020px) {{
        .main .block-container {{
          max-width: 40rem;
        }}
        .main {{
          margin: 0;
          border-radius: 0;
        }}
      }}

      /* Laptops and small displays */
      @media screen and (min-width: 1020px) and (max-width: 1366px) {{
        .main .block-container {{
          max-width: 52rem;
        }}
        [data-baseweb=select] {{
          font-size: .95rem;
        }}
        .main {{
          margin-right: 300px;
        }}
      }}

      /* Large monitors */
      @media screen and (min-width: 1366px) and (max-width: 1600px) {{
        .main .block-container {{
          max-width: 60rem;
        }}
        .main {{
          margin-right: 350px;
        }}
      }}

      /* Very large monitors */
      @media screen and (min-width: 1600px) {{
        .main .block-container {{
          max-width: 65rem;
        }}
        .main {{
          margin-right: 450px;
        }}
      }}
    </style>
  """
  st.markdown(shared_styles, unsafe_allow_html=True)
