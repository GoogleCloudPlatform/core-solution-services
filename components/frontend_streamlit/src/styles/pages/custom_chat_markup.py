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
      .main .block-container {{
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
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child {{
        flex-direction: column;
        position: fixed;
        right: 12px;
        top: 12px;
        gap: 0;
        max-height: calc(100% - 24px);
        flex-wrap: nowrap;
        overflow: hidden;
        border-radius: 12px;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="column"] {{
        width: 100%;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="stExpanderDetails"] {{
        max-height: 93vh;
        overflow-y: scroll;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="stExpander"] {{
        margin-left: 0;
        padding-bottom: 12px;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="stExpander"] [data-testid="stVerticalBlock"] {{
        gap: .5rem;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="stExpander"] p:has(a) {{
        white-space: nowrap;
        overflow: hidden;
        text-overflow: clip;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="stExpander"] p:has(strong > a) {{
        white-space: normal;
        overflow: visible;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="stExpander"] hr {{
        margin-top: .75em;
        margin-bottom: 1.25em;
      }}
      .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child [data-testid="stExpanderDetails"] [data-testid="element-container"]:has(hr):last-child {{
        display: none;
      }}

      pre {{
        background-color: {colors['light_fill']};
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
        background-color: {colors['light_fill']};
      }}

      /* Text input styling */
      [data-testid="textInputRootElement"] > div:nth-child(1) {{
        background-color: {colors['light_fill']};
      }}
      [data-testid="textInputRootElement"] {{
        background-color: {colors['light_fill']};
        border: 1px solid {colors['border_primary']};
        transition: border-width 0.2s ease-in;
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
        color: {colors['dim_text']} !important;
        background-color: transparent !important;
      }}
      .main [data-testid="stFormSubmitButton"] button:hover {{
        color: {colors['tint_primary']} !important;
      }}
      .main [data-testid="stFormSubmitButton"] div::after {{
        content: url('{icon_base}send-outline-rounded.svg?color=%234285f4&width=32&height=32');
        content: url('{icon_base}send-outline-rounded.svg?color=%234a4d50&width=32&height=32');
      }}
      [data-testid="stForm"] [data-testid="column"]:has(input:focus) + [data-testid="column"] [data-testid="stFormSubmitButton"] div::after {{
        content: url('{icon_base}send-outline-rounded.svg?color=%234285f4&width=32&height=32');
      }}
      .main [data-testid="stFormSubmitButton"] div {{
        line-height: 1.4;
      }}

      .stSpinner {{
        margin-bottom: 68px;
        margin-left: 30px;
      }}

      /* Smartphones and small devices */
      @media screen and (max-width: 1024px) {{
        .main {{
          padding-bottom: 30px;
        }}
        .main [data-testid="stForm"] [data-testid="textInputRootElement"] input {{
          padding: 0.65rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 20px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 0;
        }}
        .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child {{
          display: none;
        }}
      }}

      /* Laptops and small displays */
      @media screen and (min-width: 1024px) and (max-width: 1366px) {{
        .main {{
          padding-bottom: 94px;
        }}
        .main [data-testid="stForm"] [data-testid="textInputRootElement"] input {{
          padding: 0.7rem;
          font-size: .96rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 30px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 1px;
        }}
        .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child {{
          width: 276px;
        }}
      }}

      /* Large monitors */
      @media screen and (min-width: 1366px) and (max-width: 1600px) {{
        .main {{
          padding-bottom: 114px;
        }}
        .main [data-testid="stForm"] [data-testid="textInputRootElement"] input {{
          padding: 0.75rem;
          font-size: .98rem;
        }}
        .main [data-testid="stForm"] [data-testid="stVerticalBlockBorderWrapper"] > div:nth-child(1) > div:nth-child(1) {{
          bottom: 30px;
        }}
        .main [data-testid="stFormSubmitButton"] button {{
          padding-bottom: 2px;
        }}
        .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child {{
          width: 326px;
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
        .block-container > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:last-child {{
          width: 426px;
        }}
      }}
    </style>
  """
  st.markdown(landing_styles, unsafe_allow_html=True)
