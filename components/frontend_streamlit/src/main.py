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
  Streamlit app main file
"""
import utils
import streamlit as st
import logging


def app():
  st.set_page_config(
      page_title="GenAI for Enterprise (GENIE)",
      page_icon="💬",
      layout="wide",
      initial_sidebar_state="expanded",
  )
  with st.sidebar:
    st.title("GENIE v1.0")

  if st.session_state.get("auth_token", None):
    st.switch_page("pages/2_Landing.py")
  else:
    # TODO: Implement the actual authentication process via API call.
    # Change this to False for testing with the login page.
    st.switch_page("pages/1_Login.py")


if __name__ == "__main__":
  app()
  logging.info("Streamlit main page rendered.")
  #./main.py is used as an entrypoint for the build,
  # which creates a page that duplicates the Login page named "main".
  utils.hide_pages(["main", "Custom_Chat"])
