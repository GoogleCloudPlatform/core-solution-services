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
    get_chat, run_agent, run_agent_plan, get_plan,
    run_agent_execute_plan)
from components.chat_history import chat_history_panel
from common.utils.logging_handler import Logger
import utils

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

CHAT_PAGE_STYLES = """
<style>
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

st.session_state.input_loading = False

Logger = Logger.get_logger(__file__)

def on_input_change():
  user_input = st.session_state.user_input
  agent_name = st.session_state.agent_name
  # Appending messages.
  st.session_state.messages.append({"HumanInput": user_input})

  # Send API to llm-service
  st.session_state.input_loading = True
  if agent_name.lower() == "chat":
    response = run_agent(agent_name, user_input,
                         chat_id=st.session_state.chat_id)

  elif agent_name.lower() == "plan":
    response = run_agent_plan(agent_name, user_input,
                              chat_id=st.session_state.chat_id)
  else:
    raise ValueError(f"agent_name {agent_name} is not supported.")

  st.session_state.input_loading = False

  st.session_state.chat_id = response["chat"]["id"]
  st.session_state.messages.append({"AIOutput": response["content"]})

  if "plan" in response:
    st.session_state.messages.append({"plan": response["plan"]})

  # Clean up input field.
  st.session_state.user_input = ""


def init_messages():
  messages = []
  if st.session_state.chat_id:
    chat_data = get_chat(st.session_state.chat_id)
    messages = chat_data["history"]
  else:
    messages.append({"AIOutput": "You can ask me anything."})
  # Initialize with chat history if any.
  st.session_state.setdefault("messages", messages)


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
  init_messages()

  # Create a placeholder for all chat history.
  chat_placeholder = st.empty()
  with chat_placeholder.container():
    index = 1
    for item in st.session_state.messages:
      Logger.info(item)

      if "HumanInput" in item:
        with st.chat_message("user"):
          st.write(item["HumanInput"], is_user=True, key=f"human_{index}")

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

      index = index + 1

  st.text_input("User Input:", on_change=on_input_change, key="user_input")


def chat_page():
  st.title(st.session_state.agent_name + " Agent")
  st.markdown(CHAT_PAGE_STYLES, unsafe_allow_html=True)

  # List all existing chats if any. (data model: UserChat)
  chat_history_panel()

  if st.session_state.input_loading:
    st.spinner("Sending prompt to Agent...")

  # Set up columns to mimic a right-side sidebar
  main_container = st.container()
  with main_container:
    chat_content()


if __name__ == "__main__":
  #./main.py is used as an entrypoint for the build,
  # which creates a page that duplicates the Login page named "main".
  utils.hide_pages(["main"])
  utils.init_api_base_url()
  chat_page()
