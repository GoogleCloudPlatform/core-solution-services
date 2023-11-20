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
  Streamlit app Query Engine Build Page
"""
# pylint: disable=invalid-name
import streamlit as st
from api import (build_query_engine, get_all_embedding_types,
                 get_all_vector_stores)
import utils

# For development purpose:
params = st.experimental_get_query_params()
st.session_state.auth_token = params.get("auth_token", [None])[0]

def build_clicked(engine_name:str, doc_url:str,
                  embedding_type:str, vector_store:str):
  build_query_engine(engine_name, doc_url, embedding_type, vector_store)

def qengine_build_page():
  placeholder = st.empty()

  # Get all embedding types as a list
  embedding_types = get_all_embedding_types()

  # Get all vector stores as a list
  vector_store_list = get_all_vector_stores()

  with placeholder.form("build"):
    st.title("Build Query Engine")
    engine_name = st.text_input("Name")
    doc_url = st.text_input("Document URL")
    embedding_type = st.selectbox(
        "Emebdding:",
        embedding_types)
    vector_store = st.selectbox(
        "Vector Store:",
        vector_store_list)
    submit = st.form_submit_button("Build")
  if submit:
    build_clicked(engine_name, doc_url, embedding_type, vector_store)

if __name__ == "__main__":
  utils.init_api_base_url()
  qengine_build_page()
