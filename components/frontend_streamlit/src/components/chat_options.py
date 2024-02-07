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
Chat action buttons
"""
# pylint: disable=unused-variable
import streamlit as st
from api import (get_chat)
from styles.style_constants import colors

def handle_click(option):
  st.session_state.btn_states[option] = not st.session_state.btn_states[option]

  if option == "dislike_btn" and st.session_state.btn_states["like_btn"]:
    st.session_state.btn_states["like_btn"] = False

  if option == "like_btn" and st.session_state.btn_states["dislike_btn"]:
    st.session_state.btn_states["dislike_btn"] = False

def action_buttons(refresh_func=None):
  icon_states = {
    "like_btn": False,
    "dislike_btn": False
  }

  if "btn_states" not in st.session_state:
    st.session_state.btn_states = icon_states

  extra1, like, dislike, share, edit, translate,\
  info, refresh, more, extra2\
  = st.columns([.05, .05, .05, .05, .05, .05, .05, .05, .05, .55])

  with like:
    st.button("Like", type="primary", help="Good response",
                on_click=handle_click, args=["like_btn"])

    if st.session_state.btn_states["like_btn"]:
      like_state = "action_btn_on"
    else:
      like_state = "action_btn"

  with dislike:
    st.button("Dislike", type="primary", help="Bad response",
                on_click=handle_click, args=["dislike_btn"])

    if st.session_state.btn_states["dislike_btn"]:
      dislike_state = "action_btn_on"
    else:
      dislike_state = "action_btn"

  with share:
    st.button("Share", type="primary", help="Share & export")

  with edit:
    st.button("Edit", type="primary", help="Modify response")

  with translate:
    st.button("Translate", type="primary", help="Translate response")

  with info:
    st.button("Info", type="primary", help="Get more info")

  with refresh:
    st.button("Refresh", type="primary", help="Reload chat",
                on_click=refresh_func)

  with more:
    st.button("More", type="primary", help="More")

  icon_base = "https://api.iconify.design/material-symbols/"
  icon_size = "width=24&height=24"

  action_btn_styles = f"""
    <style>
      /* Chat options button styles */
      [data-testid="column"]:nth-child(2) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}thumb-up-outline-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}thumb-up-outline-rounded.svg?color={colors[like_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(2) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}thumb-up-outline-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}
      
      [data-testid="column"]:nth-child(3) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}thumb-down-outline-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}thumb-down-outline-rounded.svg?color={colors[dislike_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(3) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}thumb-down-outline-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}

      [data-testid="column"]:nth-child(4) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}share-outline.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}share-outline.svg?color={colors["action_btn"]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(4) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}share-outline.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}

      [data-testid="column"]:nth-child(5) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}edit-square-outline-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}edit-square-outline-rounded.svg?color={colors["action_btn"]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(5) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}edit-square-outline-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}

      [data-testid="column"]:nth-child(6) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}g-translate.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}g-translate.svg?color={colors["action_btn"]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(6) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}g-translate.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}

      [data-testid="column"]:nth-child(7) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}info-outline.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}info-outline.svg?color={colors["action_btn"]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(7) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}info-outline.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}

      [data-testid="column"]:nth-child(8) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}refresh-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}refresh-rounded.svg?color={colors["action_btn"]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(8) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}refresh-rounded.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}

      [data-testid="column"]:nth-child(9) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}more-vert.svg?color={colors["action_btn_on"]}&{icon_size}');
        content: url('{icon_base}more-vert.svg?color={colors["action_btn"]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(9) [data-testid="baseButton-primary"]:hover div::after {{
        content: url('{icon_base}more-vert.svg?color={colors["action_btn_on"]}&{icon_size}');
      }}

      [data-testid="column"]:nth-child(9) [data-testid="baseButton-primary"] {{
        padding-left: .45rem;
        padding-bottom: 0.14rem;
      }}
    </style>
  """
  st.markdown(action_btn_styles, unsafe_allow_html=True)
  