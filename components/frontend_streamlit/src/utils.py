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
import re
import streamlit as st
from streamlit_javascript import st_javascript
from common.utils.logging_handler import Logger
from config import API_BASE_URL

Logger = Logger.get_logger(__file__)

def navigate_to(url):
  nav_script = f"""
      <meta http-equiv="refresh" content="0; url='{url}'">
  """
  st.write(nav_script, unsafe_allow_html=True)

def init_api_base_url():
  api_base_url = API_BASE_URL

  if not API_BASE_URL:
    url = st_javascript(
        "await fetch('').then(r => window.parent.location.href)")
    match = re.search("(https?://)?(www\\.)?([^/]+)", (url or ""))
    if match:
      api_base_url = match.group(1) + match.group(3)

  st.session_state.api_base_url = api_base_url.rstrip("/")
  print(f"st.session_state.api_base_url = {st.session_state.api_base_url}")
