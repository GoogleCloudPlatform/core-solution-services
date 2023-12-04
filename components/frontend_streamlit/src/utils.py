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
from streamlit.runtime.scriptrunner import RerunData, RerunException
from streamlit.source_util import get_pages

def http_navigate_to(url):
  nav_script = f"""
      <meta http-equiv="refresh" content="0; url='{url}'">
  """
  st.write(nav_script, unsafe_allow_html=True)

def navigate_to(page_name):
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
          
def init_api_base_url():
  api_base_url = API_BASE_URL

  if not API_BASE_URL:
    url = st_javascript(
        "await fetch('').then(r => window.parent.location.href)")
    match = re.search("(https?://)?(www\\.)?([^/]+)", (url or ""))
    if match:
      api_base_url = match.group(1) + match.group(3)

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