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
import json
import streamlit as st
from api import (build_query_engine, get_all_embedding_types,
                 get_all_vector_stores, get_all_jobs)
from common.utils.logging_handler import Logger
import utils

Logger = Logger.get_logger(__file__)

# For development purpose:
params = st.experimental_get_query_params()
st.session_state.auth_token = params.get("auth_token", [None])[0]

def build_clicked(engine_name:str, doc_url:str,
                  embedding_type:str, vector_store:str,
                  description:str):
  build_query_engine(
    engine_name, doc_url, embedding_type, vector_store, description)

def query_engine_build_page():
  # Get all embedding types as a list
  embedding_types = get_all_embedding_types()
  # Get all vector stores as a list
  vector_store_list = get_all_vector_stores()
  # Get all query_engine_build jobs
  qe_build_jobs = get_all_jobs()
  if not qe_build_jobs:
    Logger.error("No query engine build jobs")
    st.write("No query engine build jobs")
    return
  qe_build_jobs.sort(key=lambda x: x["last_modified_time"], reverse=True)

  # Reformat list of dict to nested arrays for table.
  jobs_table_value = [[
    "Job ID", "Engine Name", "Status", "Embeddings Type", "LLM type",
    "Vector Store", "Doc URL", "Errors", "Last Modified"
  ]]
  for job in qe_build_jobs:
    input_data = json.loads(job["input_data"])
    jobs_table_value.append([
      job["name"],
      input_data.get("query_engine"),
      job["status"],
      input_data.get("embedding_type"),
      input_data.get("llm_type"),
      input_data.get("vector_store"),
      input_data.get("doc_url"),
      job.get("errors", {}).get("error_message", ""),
      job["last_modified_time"]
    ])

  st.title("Query Engine Management")
  tab1, tab2 = st.tabs(["Build Query Engine", "Job List"])

  with tab1:
    st.subheader("Build a new Query Engine")
    placeholder = st.empty()

  with tab2:
    st.subheader("Query Engine Jobs")
    st.table(jobs_table_value)

  with placeholder.form("build"):
    engine_name = st.text_input("Name")
    doc_url = st.text_input("Document URL")
    embedding_type = st.selectbox(
        "Embedding:",
        embedding_types)
    vector_store = st.selectbox(
        "Vector Store:",
        vector_store_list)
    description = st.text_area("description")

    submit = st.form_submit_button("Build")
  if submit:
    build_clicked(
      engine_name, doc_url, embedding_type, vector_store, description)


if __name__ == "__main__":
  utils.init_api_base_url()
  query_engine_build_page()
