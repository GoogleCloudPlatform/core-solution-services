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
  Streamlit app Login Page
"""
# pylint: disable=invalid-name
import streamlit as st
import utils
import api
from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)

def login_clicked(username, password):
  Logger.info(f"Logging in as {username}")
  token = api.login_user(username, password)
  if token:
    st.session_state["logged_in"] = True
    st.session_state["auth_token"] = token
    st.session_state["username"] = username
    utils.http_navigate_to("Landing")
  else:
    st.session_state["logged_in"] = False
    st.error("Invalid username or password")

def login_page():
  placeholder = st.empty()

  if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

  if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

  if not st.session_state["logged_in"]:
    st.warning("Please enter your username and password")

  with placeholder.form("login"):
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submit = st.form_submit_button("Login")
  if submit:
    login_clicked(username, password)


if __name__ == "__main__":
  utils.init_page(redirect_to_without_auth=False)
  login_page()
