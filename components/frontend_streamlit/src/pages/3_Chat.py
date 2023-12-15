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
  Streamlit app Chat Page
"""
# pylint: disable=invalid-name
import re
import streamlit as st
from api import (
    get_chat, run_dispatch, get_plan,
    run_agent_execute_plan)
from components.chat_history import chat_history_panel
from common.utils.logging_handler import Logger
import utils

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

CHAT_PAGE_STYLES = """
<style>
  .stButton[data-testid="stFormSubmitButton"] {
    display: none;
  }
  .stTextInput input {
    color: #555555;
    -webkit-text-fill-color: black;
  }
  .stTextArea label {
    display: none !important;
  }
  .stTextArea textarea {
    color: #555555;
    -webkit-text-fill-color: black;
  }
</style>
"""

Logger = Logger.get_logger(__file__)


def on_submit(user_input):
  """ Run dispatch agent when adding an user input prompt """
  # Appending messages.
  st.session_state.messages.append({"HumanInput": user_input})

  with st.spinner("Loading..."):
    # Send API to llm-service
    response = run_dispatch(user_input,
                            chat_id=st.session_state.get("chat_id"))
    st.session_state.default_route = response.get("route", None)

    if not st.session_state.chat_id:
      st.session_state.chat_id = response["chat"]["id"]
      st.session_state.user_chats.insert(0, response["chat"])

    # TODO: Currently the AIOutput vs content are inconsistent across
    # API response and in a UserChat history.
    if "content" in response:
      response["AIOutput"] = response["content"]
    del response["chat"]

    st.session_state.messages.append(response)


def format_ai_output(text):
  Logger.info(text)

  text = ansi_escape.sub("", text)
  text = text.replace("> Entering new AgentExecutor chain",
                      "**Entering new AgentExecutor chain**")
  text = text.replace("Observation:", "---\n**Observation**:")
  text = text.replace("Thought:", "- **Thought**:")
  text = text.replace("Action:", "- **Action**:")
  text = text.replace("Action Input:", "- **Action Input**:")
  text = text.replace("> Finished chain:", "**Finished chain**:")
  return text

def chat_content():
  if st.session_state.debug:
    with st.expander("DEBUG: session_state"):
      st.write(st.session_state.get("landing_user_input"))
      st.write(st.session_state.get("messages"))

  if st.session_state.chat_id:
    st.write(f"Chat ID: **{st.session_state.chat_id}**")

  # Create a placeholder for all chat history.
  reference_index = 0
  chat_placeholder = st.empty()
  with chat_placeholder.container():
    index = 1
    for item in st.session_state.messages:
      Logger.info(item)

      if "HumanInput" in item:
        with st.chat_message("user"):
          st.write(item["HumanInput"], is_user=True, key=f"human_{index}")

      if "route_name" in item:
        route_name = item["route_name"]
        with st.chat_message("ai"):
          st.write(
              f"Using route **`{route_name}`** to respond.",
              key=f"ai_{index}",
          )

      if item.get("route_logs", "").strip() != "":
        with st.expander("Expand to see Agent's thought process"):
          st.write(item["route_logs"])

      if "AIOutput" in item:
        with st.chat_message("ai"):
          ai_output = item["AIOutput"]
          ai_output = format_ai_output(ai_output)
          st.write(
              ai_output,
              key=f"ai_{index}",
              unsafe_allow_html=False,
              is_table=False,  # TODO: Detect whether an output content type.
          )

      # Append all resources.
      if "resources" in item:
        with st.chat_message("ai"):
          for name, link in item["resources"].items():
            st.markdown(f"Resource: [{name}]({link})")

      # Append all query references.
      if "query_references" in item:
        with st.chat_message("ai"):
          st.write("References:")
          for reference in item["query_references"]:
            document_url = reference["document_url"]
            document_text = reference["document_text"]
            st.markdown(f"**{reference_index}.** [{document_url}]({document_url})")
            st.text_area(
              f"Reference: {document_url}",
              document_text,
              key=f"ref_{reference_index}")
            reference_index = reference_index + 1
          st.divider()

      if "plan" in item:
        with st.chat_message("ai"):
          index = 1

          plan = get_plan(item["plan"]["id"])
          Logger.info(plan)

          for step in plan["plan_steps"]:
            st.text_area(f"step-{index}", step["description"],
                         height=30, disabled=True,
                         label_visibility="hidden")
            index = index + 1

          plan_id = plan["id"]
          if st.button("Execute this plan", key=f"plan-{plan_id}"):
            with st.spinner("Executing the plan..."):
              output = run_agent_execute_plan(
                plan_id=plan_id,
                chat_id=st.session_state.chat_id,
                auth_token=st.session_state.auth_token)
            st.session_state.messages.append({
              "AIOutput": f"Plan executed successfully. (plan_id={plan_id})",
            })

            agent_process_output = output.get("agent_process_output", "")
            agent_process_output = ansi_escape.sub("", agent_process_output)
            st.session_state.messages.append({
              "AIOutput": agent_process_output,
            })

      if item.get("agent_logs", "").strip() != "":
        with st.expander("Expand to see Agent's thought process"):
          st.write(item["agent_logs"])

      index = index + 1


def init_messages():
  """ Init all messages """
  if st.session_state.chat_id:
    chat_data = get_chat(st.session_state.chat_id)
    st.session_state.messages = chat_data["history"]
  elif not st.session_state.get("messages", None):
    st.session_state.messages = [{
      "AIOutput": "You can ask me anything."
    }]


def chat_page():
  st.markdown(CHAT_PAGE_STYLES, unsafe_allow_html=True)
  st.title("Chat")

  # List all existing chats if any. (data model: UserChat)
  chat_history_panel()

  content_placeholder = st.container()

  with st.form("user_input_form", border=False, clear_on_submit=True):
    col1, col2 = st.columns([5, 1])
    with col1:
      user_input = st.text_input("User Input", key="user_input")
      submitted = st.form_submit_button("Submit")
    with col2:
      st.session_state.default_route = st.selectbox(
          "Chat Mode", ["Auto", "Chat", "Plan", "Query"])

    if submitted:
      on_submit(user_input)

  # Pass prompt from the Landing page if any.
  landing_user_input = st.session_state.get("landing_user_input", None)
  if not st.session_state.chat_id and landing_user_input:
    on_submit(st.session_state.landing_user_input)
    st.session_state.landing_user_input = ""

  with content_placeholder:
    chat_content()


if __name__ == "__main__":
  utils.init_page()
  init_messages()
  chat_page()
