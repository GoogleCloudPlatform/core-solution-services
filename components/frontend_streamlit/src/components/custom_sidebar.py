# Copyright 2024 Google LLC
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
Custom sidebar component for references and plan steps
"""

import re
import streamlit as st
from api import (get_plan, get_all_routing_agents)
from components.chat_model_select import chat_model_select

def dedup_list(items, dedup_key):
  items_dict = {}
  for item in items:
    items_dict[item[dedup_key]] = item
  return list(items_dict.values())

def render_cloud_storage_url(url):
  """ Parse a cloud storage url. """
  if url[:3] == "/b/":
    url = url.replace("/b/", "https://storage.googleapis.com/")
    url = url.replace("/o/", "/")
  return url

def custom_sidebar(refresh_func=None):
  ref_col, plan_col, options = st.columns(3)

  with ref_col:
    has_refs = False
    for item in st.session_state.messages:
      if item.get("query_references", None):
        has_refs = True
        with st.expander("References", expanded=True):
          for reference in dedup_list(item["query_references"], "chunk_id"):
            # site_name = "Medicaid"
            document_url = render_cloud_storage_url(reference["document_url"])
            document_text = reference["document_text"]
            markdown_content = re.sub(
                r"<b>(.*?)</b>", r"**\1**", document_text, flags=re.IGNORECASE)

            st.write("**Site:**")
            st.markdown(f"[{document_url}]({document_url})")
            st.write("**Overview:**")
            st.markdown(markdown_content)

            st.divider()

      if item.get("db_result", None):
        with st.expander("References", expanded=True):
          result_index = 1

          # Clean up empty rows.
          db_result = []
          for result in item["db_result"]:
            if len(result.keys()) > 0:
              db_result.append(result)

          if len(db_result) > 0:
            has_refs = True
            for result in db_result:
              values = [str(x) for x in list(result.values())]
              if len(values) > 0:
                markdown_content = f"{result_index}. **{values[0]}**"
                markdown_content += " - " + ", ".join(values[1:])

                st.markdown(markdown_content)
              result_index = result_index + 1

    if has_refs is False:
      with st.expander("References", expanded=False):
        st.write("No references to display")

  with plan_col:
    for item in st.session_state.messages:
      if "plan" in item:
        plan = get_plan(item["plan"]["id"])
        with st.expander("Plan Steps"):
          for step in plan["plan_steps"]:
            st.write(step["description"])

  with options:
    with st.expander("Advanced Settings"):
      chat_model_select()

      routing_agents = get_all_routing_agents()
      routing_agent_names = list(routing_agents.keys())
      chat_modes = routing_agent_names + ["Chat", "Plan", "Query", "DbAgent"]
      chat_mode_index = 0

      if st.session_state.default_route:
        while chat_mode_index < len(chat_modes):
          if st.session_state.default_route == chat_modes[chat_mode_index]:
            break
          chat_mode_index += 1
        if chat_mode_index >= len(chat_modes):
          chat_mode_index = 0

      st.session_state.default_route = st.selectbox(
          "Chat Mode", chat_modes, index=chat_mode_index)

      if refresh_func:
        st.button("Refresh", on_click=refresh_func)
