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
Main styles for the chat page
"""

import streamlit as st
from styles.style_constants import colors
from styles.shared_styles import main_styles

def chat_theme():
  main_styles()

  landing_styles = f"""
    <style>
      /* Hidden elements */
      .main [data-testid="stFormSubmitButton"] button p {{
        display: none;
      }}
      .main [data-testid="stVerticalBlock"] {{
        gap: 0;
      }}

      /* Heading styles */
      .main .stHeadingContainer h1 {{
        font-family: Arial;
        color: {colors['text_primary']};
      }}

      /* Content header positioning */
      .main [data-testid="block-container"] {{
        overflow: auto;
      }}
      .main [data-testid="stHorizontalBlock"]:has(img),
      .main .stHeadingContainer {{
        position: fixed;
      }}
      .main [data-testid="stHorizontalBlock"]:has(img) {{
        width: 100%;
      }}
      
      /* Text input positioning */
      .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
        position: fixed;
        bottom: 50px;
      }}

      /* Text area styling */
      .stTextArea {{
        padding-bottom: 1rem;
      }}
      [data-baseweb="textarea"] [data-baseweb="base-input"],
      [data-baseweb="textarea"] {{
        background-color: {colors['light_fill']};
        border: none;
      }}
      .stTextArea textarea {{
        color: {colors['input_text']};
        -webkit-text-fill-color: {colors['input_text']};
      }}
      .stTextArea label {{
        display: none !important;
      }}

      div[data-testid='stExpander'] {{
        margin-left: 3em;
      }}

      /* Chat styling */
      [data-testid="chatAvatarIcon-user"] {{
        background-color: {colors['tint_primary']};
      }}
      .stChatMessage:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: {colors['light_fill']};
        margin-top: 10px;
      }}

      /* Text input styling */
      [data-testid="textInputRootElement"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
      }}
      [data-testid="textInputRootElement"] {{
        background-color: {colors['light_fill']};
        border: 1px solid {colors['border_primary']};
        transition: border-color 0.1s ease-in, border-width 0.2s ease-in;
        border-radius: 18px;
      }}
      [data-testid="textInputRootElement"]:has(input:focus) {{
        border: 2px solid {colors['tint_primary']};
      }}
      [data-testid="textInputRootElement"] input {{
        color: {colors['input_text']};
        -webkit-text-fill-color: {colors['input_text']};
      }}

      /* Input button styling */
      .main [data-testid="stFormSubmitButton"] button {{
        border: none;
        padding-left: 0;
        float: right;
        color: {colors['dim_text']} !important;
        background-color: transparent !important;
      }}
      .main [data-testid="stFormSubmitButton"] button:hover {{
        color: {colors['tint_primary']} !important;
      }}
      .main [data-testid="stFormSubmitButton"] button::after {{
        content: "➤";
        font-size: 26px;
        transition: color 0.25s ease-in;
      }}

      /* Smartphones and small devices */
      @media screen and (max-width: 1024px) {{
        .main {{
          padding-bottom: 30px;
        }}
        .main .stHeadingContainer h1 {{
          font-size: 26px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.7rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 20px;
        }}
      }}

      /* Laptops and small displays */
      @media screen and (min-width: 1024px) and (max-width: 1366px) {{
        .main {{
          padding-bottom: 90px;
          padding-top: 145px;
        }}
        .main .stHeadingContainer h1 {{
          font-size: 30px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.72rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 44px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 2px;
        }}
        .main [data-testid="stHorizontalBlock"]:has(img) {{
          top: 80px;
          max-width: 50rem;
        }}
        .main .stHeadingContainer {{
          top: 136px;
        }}
        [data-baseweb="popover"] {{
          top: -55.5px;
        }}
      }}

      /* Large monitors */
      @media screen and (min-width: 1366px) and (max-width: 1600px) {{
        .main {{
          padding-bottom: 110px;
          padding-top: 180px;
        }}
        .main .stHeadingContainer h1 {{
          font-size: 38px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.83rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 54px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 5px;
        }}
        .main [data-testid="stHorizontalBlock"]:has(img) {{
          top: 104px;
          max-width: 55.5rem;
        }}
        .main .stHeadingContainer {{
          top: 165px;
        }}
        [data-baseweb="popover"] {{
          top: -71.5px;
        }}
      }}

      /* Very large monitors */
      @media screen and (min-width: 1600px) {{
        .main {{
          padding-bottom: 120px;
          padding-top: 190px;
        }}
        .main .stHeadingContainer h1 {{
          font-size: 42px;
        }}
        [data-testid="textInputRootElement"] input {{
          padding: 0.85rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 64px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 4px;
        }}
        .main [data-testid="stHorizontalBlock"]:has(img) {{
          top: 104px;
          max-width: 60rem;
        }}
        .main .stHeadingContainer {{
          top: 165px;
        }}
        [data-baseweb="popover"] {{
          top: -81px;
        }}
      }}
    </style>
  """
  st.markdown(landing_styles, unsafe_allow_html=True)
