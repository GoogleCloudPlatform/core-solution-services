# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
  Streamlit app utils file
"""
import streamlit as st
from common.utils.logging_handler import Logger
from config import API_BASE_URL, APP_BASE_PATH
from streamlit.runtime.scriptrunner import RerunData, RerunException
from streamlit.source_util import get_pages
from urllib.parse import urlparse
from api import validate_auth_token

Logger = Logger.get_logger(__file__)

def http_navigate_to(url, query_params={}):
  """ Navigate to a specific URL. However, this will lose all session_state. """

  query_params_from_session = ["auth_token", "debug"]
  query_params_list = [
      (x + "=" +str(st.session_state.get(x, ""))) \
      for x in query_params_from_session]

  for key, value in query_params.items():
    query_params_list.append(f"{key}={value}")

  query_param_str = "&".join(query_params_list)

  url_ojb = urlparse(url)
  url = f"{url}?{query_param_str}&{url_ojb.query}"

  nav_script = f"""
      <meta http-equiv="refresh" content="0; url='{url}'">
  """
  st.write(nav_script, unsafe_allow_html=True)


def navigate_to(page_name):
  """ Navigate to a specific page and keep session_state. """
  def standardize_name(name: str) -> str:
    return name.lower().replace("_", " ")
  page_name = standardize_name(page_name)
  pages = get_pages("main.py")

  for page_hash, config in pages.items():
    if standardize_name(config["page_name"]) == page_name:
      raise RerunException(
        RerunData(
          page_script_hash=page_hash,
          page_name=page_name,
        )
      )


def init_session_state():
  query_params = st.experimental_get_query_params()

  # If set query_param "debug=true"
  if query_params.get("debug", [""])[0].lower() == "true":
    st.session_state.debug = True

  error_msg = query_params.get("error_msg", [""])[0]
  if error_msg:
    st.session_state.error_msg = error_msg

  # Try to get a state var from query parameter.
  states_to_init = [
    "auth_token", "chat_id", "agent_name", "debug"
  ]
  for state_name in states_to_init:
    if not st.session_state.get(state_name, None):
      st.session_state[state_name] = query_params.get(state_name, [""])[0]

def init_page(redirect_to_without_auth=True):
  init_session_state()

  # Check auth_token
  auth_token = st.session_state.get("auth_token", None)
  if auth_token and not validate_auth_token():
    st.session_state.error_msg = \
        "Unauthorized or session expired. " \
        f"Please [Login]({APP_BASE_PATH}/Login) again."

  error_msg = st.session_state.get("error_msg", "")
  if error_msg:
    with st.container():
      st.write(error_msg, unsafe_allow_html=True)

  # If still not getting auth_token, redirect back to Login page.
  if redirect_to_without_auth and not st.session_state.get("auth_token", None):
    navigate_to("Login")

  #./main.py is used as an entrypoint for the build,
  # which creates a page that duplicates the Login page named "main".
  hide_pages(["main"])

  api_base_url = API_BASE_URL
  st.session_state.api_base_url = api_base_url.rstrip("/")
  Logger.info("st.session_state.api_base_url = "
              f"{st.session_state.api_base_url}")

def hide_pages(hidden_pages: list[str]):
  styling = ""
  current_pages = get_pages("")
  section_hidden = False

  for idx, val in enumerate(current_pages.values()):
    page_name = val.get("page_name")

    if val.get("is_section"):
      # Set whole section as hidden
      section_hidden = page_name in hidden_pages
    elif not val.get("in_section"):
      # Reset whole section hiding if we hit a page thats not in a section
      section_hidden = False
    if page_name in hidden_pages or section_hidden:
      styling += f"""
        div[data-testid=\"stSidebarNav\"] li:nth-child({idx + 1}) {{
            display: none;
        }}
      """

  styling = f"""
    <style>
        {styling}
    </style>
  """
  st.write(
    styling,
    unsafe_allow_html=True,
  )
