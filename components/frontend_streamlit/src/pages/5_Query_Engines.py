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
import moment
import streamlit as st
from api import (build_query_engine, update_query_engine,
                 get_all_embedding_types,
                 get_all_vector_stores, get_all_query_engines,
                 get_all_jobs)
from common.utils.logging_handler import Logger
from common.config import PROJECT_ID
import utils

Logger = Logger.get_logger(__file__)

def submit_build(engine_name:str, doc_url:str,
                  embedding_type:str, vector_store:str,
                  description:str):
  try:
    output = build_query_engine(
      engine_name, doc_url, embedding_type, vector_store, description)

    if output.get("success") is True:
      job_id = output["data"]["job_name"]
      st.success(f"Query Engine build job created. Job ID: {job_id}")
    else:
      st.error(output.get("message"))

  except RuntimeError as e:
    st.error(e)

def submit_update(query_engine_id:str, name:str, description:str):
  output = update_query_engine(query_engine_id, name, description)

  if output.get("success") is True:
    st.success(f"Query Engine {name} updated successfully.")
  else:
    st.error(output["message"])


def query_engine_build_page():
  # Get all embedding types as a list
  embedding_types = get_all_embedding_types()
  # Get all vector stores as a list
  vector_store_list = get_all_vector_stores()

  # Prepare table values
  qe_list = get_all_query_engines()
  qe_build_jobs = get_all_jobs()

  st.title("Query Engine Management")
  tab_qe, tab_jobs, tab_create_qe = st.tabs([
    "Query Engines",
    "Job List",
    "Build Query Engine",
  ])

  with tab_qe:
    st.subheader("Query Engines")
    if not qe_list:
      Logger.error("No query engine found.")
      st.write("No query engine found.")
      return

    for qe in qe_list:
      data = [[key, value] for key, value in qe.items()]
      summary = f"{qe['llm_type']}, {qe['embedding_type']}, " \
                f"vector_store:{qe['vector_store']}"
      with st.expander(f"**{qe['name']}** - {summary}"):
        st.table(data)
        with st.form(qe["name"]):
          description = st.text_area("Description", qe["description"])
          submit = st.form_submit_button("Update")
        if submit:
          submit_update(qe["id"], qe["name"], description)

  with tab_jobs:
    st.subheader("Query Engine Jobs")

    if not qe_build_jobs:
      Logger.error("No query engine build jobs")
      st.write("No query engine build jobs")
      return

    for job in qe_build_jobs:
      created_at = moment.date(
          job["created_time"]).format("YYYY-M-D h:m A")
      summary_data = [
        ["Job ID", job["id"]],
        ["Status", job["status"]],
        ["Created at", created_at],
        ["Errors", job.get("errors", {}).get("error_message", "")]
      ]
      input_data = json.loads(job["input_data"])
      data = [[key, value] for key, value in input_data.items()]
      query_engine = input_data['query_engine'].strip()
      status = job["status"]
      icon = "🔄"
      if status == "succeeded":
        icon = "✅"
      elif status == "failed":
        icon = "❌"

      with st.expander(
          f"**{icon} [{job['status']}]** QE: {query_engine} - " \
          f"Job created at {created_at}"):
        # FIXME: Add this to the backend data model.
        job_url = "https://console.cloud.google.com/kubernetes/job/" \
                  f"us-central1/main-cluster/default/{job['id']}/details" \
                  f"?project={PROJECT_ID}"
        st.write(f"[Link to Kubernetes Job]({job_url})")
        st.table(summary_data + data)

        submit = st.button("Re-run this job", key=f"rerun-job-{job['id']}")
        if submit:
          submit_build(
            input_data["query_engine"],
            input_data["doc_url"],
            input_data["embedding_type"],
            input_data["vector_store"],
            input_data["description"])
          st.toast("Job re-submitted with query engine: {job['query_engine']}")

  with tab_create_qe:
    st.subheader("Build a new Query Engine")
    placeholder_build_qe = st.empty()

  with placeholder_build_qe.form("build"):
    engine_name = st.text_input("Name")
    doc_url = st.text_input("Document URL")
    embedding_type = st.selectbox(
        "Embedding:",
        embedding_types)
    vector_store = st.selectbox(
        "Vector Store:",
        vector_store_list)
    description = st.text_area("Description")

    submit = st.form_submit_button("Build")
  if submit:
    submit_build(
      engine_name, doc_url, embedding_type, vector_store, description)


if __name__ == "__main__":
  utils.init_page()
  query_engine_build_page()
