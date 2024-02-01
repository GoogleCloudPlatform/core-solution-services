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
from styles.style_constants import colors, decoration
from styles.custom_shared_styles import main_styles

def custom_chat_theme():
  main_styles()
  icon_base = "https://api.iconify.design/material-symbols/"

  landing_styles = f"""
    <style>
      /* Main container styles */
      .stApp {{
        background-color: {colors['casey_tint']};
      }}
      .main {{
        background-color: {colors['light_fill']};
        padding-top: 5px;
      }}

      /* Hidden elements */
      .main [data-testid="stFormSubmitButton"] button p {{
        display: none;
      }}
      .main [data-testid="stVerticalBlock"] {{
        gap: 0;
      }}
      [data-testid="collapsedControl"] {{
        display: none;
      }}

      /* Main text content styles */
      .main p {{
        color: {colors['text_primary']};
      }}

      .main .stButton button p {{
        color: {colors['light_fill']} !important;
      }}

      /* Chat options button styles */
      .main .stButton [data-testid="baseButton-primary"] {{
        background-color: transparent;
        border: none;

        &:hover {{
          background-color: transparent;
        }}
      }}
      .main [data-testid="baseButton-primary"] p {{
        display: none;
      }}
      .main [data-testid="baseButton-primary"] div {{
        line-height: 0;
      }}

      /* Main container scroll positioning */
      .main [data-testid="block-container"] {{
        overflow: auto;
      }}

      /* Text area styling */
      .stTextArea {{
        padding-bottom: 1rem;
      }}
      [data-baseweb="textarea"] [data-baseweb="base-input"],
      [data-baseweb="textarea"] {{
        background-color: {colors['casey_tint']};
        border: none;
      }}
      .stTextArea textarea {{
        color: {colors['input_text']};
        -webkit-text-fill-color: {colors['input_text']};
        caret-color: {colors['input_text']};
        cursor: default;
      }}
      .stTextArea label {{
        display: none !important;
      }}

      /* Expander styling */
      .main [data-testid="stExpander"] details {{
        border-color: {colors['light_fill']};
        border-radius: {decoration['border_radius']};
        background-color: {colors['light_fill']};
        color: rgb(49, 51, 63);
      }}
      .main [data-testid="stExpander"] summary p {{
        font-family: Arial;
        color: {colors['dim_text']} !important;
        font-weight: 600;
        font-size: .925rem;
      }}
      [data-testid="stExpander"] {{
        margin-left: 2.8em;
      }}
      .main [data-testid="stExpander"] [data-testid="stText"] {{
        font-family: Arial;
        text-wrap: wrap;
      }}
      .main [data-testid="stExpander"] summary span {{
        flex-grow: 0;
      }}
      .main [data-testid="stExpander"] [data-testid="stVerticalBlock"] {{
        gap: 1rem;
      }}
      .main [data-testid="stExpander"] svg {{
        margin-top: 1.5px;
        margin-left: 3px;
        color: {colors['dim_text']};
      }}
      .main [data-testid="stExpander"] summary:hover svg {{
        fill: {colors['dim_text']};
      }}

      /* References styling */
      [data-testid="stForm"] + div {{
        flex-direction: column;
        position: fixed;
        width: 426px;
        right: 12px;
        top: 12px;
        gap: 0;
      }}
      [data-testid="stForm"] + div [data-testid="column"] {{
        width: 100%;
      }}
      [data-testid="stForm"] + div [data-testid="stExpander"] {{
        margin-left: 0;
        padding-bottom: 12px;
      }}
      [data-testid="stForm"] + div [data-testid="stExpander"] [data-testid="stVerticalBlock"] {{
        gap: .5rem;
      }}
      [data-testid="stForm"] + div [data-testid="stExpander"] a {{
        color: {colors['tint_primary']};
      }}
      [data-testid="stForm"] + div [data-testid="stExpander"] a::after {{
        content: url('{icon_base}open-in-new-rounded.svg?height=17&color=%234285f4');
        margin-left: 7px;
        vertical-align: sub;
      }}
      [data-testid="stForm"] + div [data-testid="stExpander"] hr {{
        margin-top: 1em;
        margin-bottom: 1.5em;
      }}

      /* Chat styling */
      [data-testid="chatAvatarIcon-user"],
      [data-testid="chatAvatarIcon-assistant"] {{
        background-color: transparent;
        color: {colors['tint_primary']};
        line-height: .5;
      }}
      .stChatMessage {{
        gap: 0.8rem;
      }}
      [data-testid="chatAvatarIcon-user"]::after {{
        content: url('{icon_base}face-outline.svg?height=28&color=%234285f4');
      }}
      [data-testid="chatAvatarIcon-assistant"] svg,
      [data-testid="chatAvatarIcon-user"] svg {{
        display: none;
      }}
      [data-testid="chatAvatarIcon-assistant"]::after {{
        content: url('https://api.iconify.design/logos/google-bard-icon.svg?height=28');
      }}
      .stChatMessage:has([data-testid="chatAvatarIcon-user"]) {{
        background-color: {colors['casey_tint']};
        margin-top: 10px;
      }}
      [data-testid="stChatMessageContent"] code {{
        background-color: {colors['casey_tint']};
      }}

      /* Text input styling */
      [data-testid="textInputRootElement"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
      }}
      [data-testid="textInputRootElement"] {{
        background-color: {colors['light_fill']};
        border: 1px solid {colors['border_primary']};
        transition: border-color 0.1s ease-in, border-width 0.2s ease-in;
      }}
      [data-testid="textInputRootElement"]:has(input:focus) {{
        border: 2px solid {colors['tint_primary']};
      }}
      [data-testid="textInputRootElement"] input {{
        color: {colors['input_text']};
        -webkit-text-fill-color: {colors['input_text']};
        caret-color: {colors['input_text']};
      }}
      [data-testid="stTextInput"] label p {{
        font-size: 15px;
      }}

      /* Bottom text input styles and positioning */
      .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
        position: fixed;
        bottom: 50px;
      }}
      .main [data-testid="stForm"] [data-testid="textInputRootElement"] {{
        border-radius: 18px;
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
      .main [data-testid="stFormSubmitButton"] div::after {{
        content: url('{icon_base}send-outline-rounded.svg?color=%234a4d50&width=32&height=32');
      }}
      .main [data-testid="stFormSubmitButton"] div {{
        line-height: 1.4;
      }}

      .stSpinner {{
        margin-bottom: 68px;
        margin-left: 5px;
      }}

      /* Smartphones and small devices */
      @media screen and (max-width: 1024px) {{
        .main {{
          padding-bottom: 30px;
        }}
        .main [data-testid="stForm"] [data-testid="textInputRootElement"] input {{
          padding: 0.7rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 20px;
        }}
      }}

      /* Laptops and small displays */
      @media screen and (min-width: 1024px) and (max-width: 1366px) {{
        .main {{
          padding-bottom: 94px;
        }}
        .main [data-testid="stForm"] [data-testid="textInputRootElement"] input {{
          padding: 0.72rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 20px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 2px;
        }}
      }}

      /* Large monitors */
      @media screen and (min-width: 1366px) and (max-width: 1600px) {{
        .main {{
          padding-bottom: 114px;
        }}
        .main [data-testid="stForm"] [data-testid="textInputRootElement"] input {{
          padding: 0.83rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 30px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 5px;
        }}
      }}

      /* Very large monitors */
      @media screen and (min-width: 1600px) {{
        .main {{
          padding-bottom: 124px;
        }}
        .main [data-testid="stForm"] [data-testid="textInputRootElement"] input {{
          padding: 0.85rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 40px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 4px;
        }}
      }}
    </style>
  """
  st.markdown(landing_styles, unsafe_allow_html=True)
