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

import streamlit as st
from styles.custom_style_constants import colors

def handle_click(option):
  st.session_state.btn_states[option] = not st.session_state.btn_states[option]

  if option == "dislike_btn" and st.session_state.btn_states["like_btn"] == True:
    st.session_state.btn_states["like_btn"] = False

  if option == "like_btn" and st.session_state.btn_states["dislike_btn"] == True:
    st.session_state.btn_states["dislike_btn"] = False

def action_buttons():
  icon_states = {
    "like_btn": False,
    "dislike_btn": False,
    "share_btn": False,
    "edit_btn": False,
    "translate_btn": False,
    "info_btn": False,
    "refresh_btn": False,
    "more_btn": False
  }

  if "btn_states" not in st.session_state:
    st.session_state.btn_states = icon_states

  extra1, like, dislike, share, edit, translate, info, refresh, more, extra2 = st.columns([.05, .05, .05, .05, .05, .05, .05, .05, .05, .55])

  with like:
    st.button("Like", type="primary", help="Good response", on_click=handle_click, args=["like_btn"])

    if st.session_state.btn_states["like_btn"]:
      like_state = "action_btn_on"
    else:
      like_state = "action_btn"

  with dislike:
    st.button("Dislike", type="primary", help="Bad response", on_click=handle_click, args=["dislike_btn"])

    if st.session_state.btn_states["dislike_btn"]:
      dislike_state = "action_btn_on"
    else:
      dislike_state = "action_btn"

  with share:
    st.button("Share", type="primary", help="Share & export", on_click=handle_click, args=["share_btn"])

    if st.session_state.btn_states["share_btn"]:
      share_state = "action_btn_on"
    else:
      share_state = "action_btn"

  with edit:
    st.button("Edit", type="primary", help="Modify response", on_click=handle_click, args=["edit_btn"])

    if st.session_state.btn_states["edit_btn"]:
      edit_state = "action_btn_on"
    else:
      edit_state = "action_btn"
  
  with translate:
    st.button("Translate", type="primary", help="Translate response", on_click=handle_click, args=["translate_btn"])

    if st.session_state.btn_states["translate_btn"]:
      translate_state = "action_btn_on"
    else:
      translate_state = "action_btn"

  with info:
    st.button("Info", type="primary", help="Get more info", on_click=handle_click, args=["info_btn"])

    if st.session_state.btn_states["info_btn"]:
      info_state = "action_btn_on"
    else:
      info_state = "action_btn"

  with refresh:
    st.button("Refresh", type="primary", help="Reload chat", on_click=handle_click, args=["refresh_btn"])

    if st.session_state.btn_states["refresh_btn"]:
      refresh_state = "action_btn_on"
    else:
      refresh_state = "action_btn"

  with more:
    st.button("More", type="primary", help="More", on_click=handle_click, args=["more_btn"])

    if st.session_state.btn_states["more_btn"]:
      more_state = "action_btn_on"
    else:
      more_state = "action_btn"

  icon_base = "https://api.iconify.design/material-symbols/"
  icon_size = "width=24&height=24"

  action_btn_styles = f"""
    <style>
      /* Chat options button styles */
      [data-testid="column"]:nth-child(2) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}thumb-up-outline-rounded.svg?color={colors[like_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(3) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}thumb-down-outline-rounded.svg?color={colors[dislike_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(4) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}share-outline.svg?color={colors[share_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(5) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}edit-square-outline-rounded.svg?color={colors[edit_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(6) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}g-translate.svg?color={colors[translate_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(7) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}info-outline.svg?color={colors[info_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(8) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}refresh-rounded.svg?color={colors[refresh_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(9) [data-testid="baseButton-primary"] div::after {{
        content: url('{icon_base}more-vert.svg?color={colors[more_state]}&{icon_size}');
      }}
      [data-testid="column"]:nth-child(9) [data-testid="baseButton-primary"] {{
        padding-left: .45rem;
        padding-bottom: 0.14rem;
      }}
    </style>
  """
  st.markdown(action_btn_styles, unsafe_allow_html=True)