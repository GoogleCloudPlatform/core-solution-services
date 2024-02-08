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
# pylint: disable=invalid-name,unused-variable,global-variable-not-assigned

import re
import time
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from api import (
    get_chat, run_dispatch, get_plan,
    run_agent_execute_plan, get_job,
    get_all_routing_agents, run_agent_plan, run_chat)
from components.chat_history import chat_history_panel
from components.content_header import chat_header
from styles.pages.chat_markup import chat_theme
import logging
from common.utils.config import JOB_TYPE_ROUTING_AGENT
from common.models import JobStatus
import utils

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")



REFERENCE_CSS_STYLE = """
{
  font-weight: 400;
  line-height: 1.6;
  text-size-adjust: 100%;
  -webkit-tap-highlight-color: rgba(0, 0, 0, 0);
  -webkit-font-smoothing: auto;
  color-scheme: light;
  color: rgb(49, 51, 63);
  box-sizing: border-box;
  width: 100%;
  max-width: 100%;
  border-top-left-radius: 0.5rem;
  border-bottom-left-radius: 0.5rem;
  border-top-right-radius: 0.5rem;
  border-bottom-right-radius: 0.5rem;
  overflow: scroll;
  display: inline-block;
  padding-top: 0.5rem;
  padding-bottom: 0.5rem;
  padding-left: 1rem;
  padding-right: 1rem;
  background-color: #FFFFFF;
  border: none;
  border-width: 1px;
  resize: vertical;
  min-height: 1rem;
  margin-top: 0.4rem;
}
.loader {
    width: 48px;
    height: 48px;
    border: 5px solid #FFF;
    border-bottom-color: transparent;
    border-radius: 50%;
    display: inline-block;
    box-sizing: border-box;
    animation: rotation 1s linear infinite;
}

@keyframes rotation {
  0% {
      transform: rotate(0deg);
  }
  100% {
      transform: rotate(360deg);
  }
}
"""

loader_spin_html = "<span class=\"loader\"></span>"


content_container = None
messages_container = None
spinner_container = None
on_submit_clicked = False

def on_submit(user_input):
  """ Run dispatch agent when adding an user input prompt """
  st.session_state.error_msg = None
  st.session_state.messages.append({"HumanInput": user_input})
  message_index = len(st.session_state.messages)

  with st.chat_message("user"):
    st.write(user_input, is_user=True, key=f"human_{message_index}")

  # Send API to llm-service
  default_route = st.session_state.get("default_route", None)
  routing_agents = get_all_routing_agents()
  routing_agent_names = list(routing_agents.keys())
  chat_llm_type = st.session_state.get("chat_llm_type")
  logging.info("llm_type in session %s", chat_llm_type)

  if default_route is None:
    # pick the first routing agent as default
    if routing_agent_names:
      routing_agent = routing_agent_names[0]
    else:
      routing_agent = "default"
    response = run_dispatch(user_input,
                            routing_agent,
                            chat_id=st.session_state.get("chat_id"),
                            llm_type=chat_llm_type,
                            run_as_batch_job=True)
    st.session_state.default_route = response.get("route", None)

  elif default_route in routing_agent_names:
    response = run_dispatch(user_input,
                            default_route,
                            chat_id=st.session_state.get("chat_id"),
                            llm_type=chat_llm_type,
                            run_as_batch_job=True)
    st.session_state.default_route = response.get("route", None)

  elif default_route == "Chat":
    response = run_chat(user_input,
                        chat_id=st.session_state.get("chat_id"),
                        llm_type=chat_llm_type)
  elif default_route == "Plan":
    response = run_agent_plan("Plan", user_input,
                              chat_id=st.session_state.get("chat_id"),
                              llm_type=chat_llm_type)
  else:
    st.error(f"Unsupported route {default_route}")
    response = None

  if response:
    st.session_state.chat_id = response["chat"]["id"]
    st.session_state.user_chats.insert(0, response["chat"])

    # TODO: Currently the AIOutput vs content are inconsistent across
    # API response and in a UserChat history.
    if "content" in response:
      response["AIOutput"] = response["content"]
    del response["chat"]

    # Append new message from the API response and display it.
    append_and_display_message(response)

    # If the response has a batch async job, keep pulling the job result.
    if "batch_job" in response:
      update_async_job(response["batch_job"]["id"])

def hide_loading():
  global spinner_container
  with spinner_container:
    st.write("")

def format_ai_output(text):
  text = text.strip()

  # Clean up ASCI code and text formatting code.
  text = ansi_escape.sub("", text)
  text = re.sub(r"\[1;3m", "\n", text)
  text = re.sub(r"\[[\d;]+m", "", text)

  # Reformat steps.
  text = text.replace("> Entering new AgentExecutor chain",
                      "**Entering new AgentExecutor chain**")
  text = text.replace("Task:", "- **Task**:")
  text = text.replace("Observation:", "---\n**Observation**:")
  text = text.replace("Thought:", "- **Thought**:")
  text = text.replace("Action:", "- **Action**:")
  text = text.replace("Action Input:", "- **Action Input**:")
  text = text.replace("Route:", "- **Route**:")
  text = text.replace("> Finished chain", "**Finished chain**")
  return text


def dedup_list(items, dedup_key):
  items_dict = {}
  for item in items:
    items_dict[item[dedup_key]] = item
  return list(items_dict.values())


def chat_metadata():
  if st.session_state.debug:
    with st.expander("DEBUG: session_state"):
      st.write(st.session_state.get("landing_user_input"))
      st.write(st.session_state.get("messages"))

  if st.session_state.chat_id:
    st.write(f"Chat ID: **{st.session_state.chat_id}**")


def update_async_job(job_id, loop_seconds=1, timeout_seconds=180):
  global spinner_container
  global messages_container
  start_time = time.time()

  count = 0
  time_elapsed = 0
  while time_elapsed < timeout_seconds:
    count += 1
    with spinner_container:
      with st.chat_message("ai"):
        st.write("Loading." + "." * int(count % 3),
                 is_user=True, key=f"ai_loading_{job_id}")

    job = get_job(JOB_TYPE_ROUTING_AGENT, job_id)
    # Pull the latest chat history.
    with messages_container:
      append_new_messages()

    # Breaks if the batch job doesn't exist.
    if not job:
      return

    # Refresh messages when job status is "succeeded" or "failed".
    if job["status"] == JobStatus.JOB_STATUS_SUCCEEDED.value:
      hide_loading()
      append_new_messages()
      return

    elif job["status"] == JobStatus.JOB_STATUS_FAILED.value:
      hide_loading()
      st.write("Job failed.")
      return

    time.sleep(loop_seconds)
    time_elapsed = time.time() - start_time

  # Timeout
  display_message({
    "AIOutput": f"Timed out after {timeout_seconds} seconds."
  }, len(st.session_state.messages))


def render_cloud_storage_url(url):
  """ Parse a cloud storage url. """
  if url[:3] == "/b/":
    url = url.replace("/b/", "https://storage.googleapis.com/")
    url = url.replace("/o/", "/")
  return url


def init_messages():
  """ Init all messages """
  if st.session_state.chat_id:
    chat_data = get_chat(st.session_state.chat_id)
    st.session_state.messages = chat_data["history"]
  elif not st.session_state.get("messages", None):
    display_message({
      "AIOutput": "You can ask me anything.",
    }, 0)
    st.session_state.messages = []

  index = 1
  last_batch_job = None
  for item in st.session_state.messages:
    display_message(item, index)
    if "batch_job" in item:
      last_batch_job = item["batch_job"]["job_id"]
    index += 1

  if last_batch_job:
    update_async_job(last_batch_job)


def append_new_messages():
  chat_data = get_chat(st.session_state.chat_id)
  new_messages = chat_data["history"][len(st.session_state.messages):]
  for item in new_messages:
    append_and_display_message(item)

  return new_messages


def append_and_display_message(item):
  st.session_state.messages.append(item)
  display_message(item, len(st.session_state.messages))


def display_message(item, item_index):
  if "HumanInput" in item:
    with st.chat_message("user"):
      st.write(item["HumanInput"], is_user=True, key=f"human_{item_index}")

  if "route_name" in item and "AIOutput" not in item:
    route_name = item["route_name"]
    with st.chat_message("ai"):
      st.write(
          f"Using route **`{route_name}`** to respond.",
          key=f"ai_{item_index}",
      )

  route_logs = item.get("route_logs", None)
  if route_logs and route_logs.strip() != "":
    with st.expander("Expand to see Agent's thought process"):
      st.write(format_ai_output(route_logs))

  if "AIOutput" in item:
    with st.chat_message("ai"):
      ai_output = item["AIOutput"]
      ai_output = format_ai_output(ai_output)
      st.write(
          ai_output,
          key=f"ai_{item_index}",
          unsafe_allow_html=False,
          is_table=False,  # TODO: Detect whether an output content type.
      )

  # Append all query references.
  if item.get("db_result", None):
    with st.chat_message("ai"):
      st.write("Query result:")
      result_index = 1

      # Clean up empty rows.
      db_result = []
      for result in item["db_result"]:
        if len(result.keys()) > 0:
          db_result.append(result)

      if len(db_result) > 0:
        for result in db_result:
          values = [str(x) for x in list(result.values())]
          if len(values) > 0:
            markdown_content = f"{result_index}. **{values[0]}**"
            markdown_content += " - " + ", ".join(values[1:])
            with stylable_container(
              key=f"ref_{result_index}",
              css_styles=REFERENCE_CSS_STYLE
            ):
              st.markdown(markdown_content)
          result_index = result_index + 1

      else:
        with stylable_container(
          key=f"ref_{result_index}",
          css_styles=REFERENCE_CSS_STYLE
        ):
          st.markdown("No result found.")

  # Append all resources.
  if item.get("resources", None):
    with st.chat_message("ai"):
      for name, link in item["resources"].items():
        st.markdown(f"Resource: [{name}]({link})")

  # Append all query references.
  if item.get("query_references", None):
    with st.chat_message("ai"):
      st.write("References:")
      reference_index = 1
      for reference in dedup_list(item["query_references"], "chunk_id"):
        document_url = render_cloud_storage_url(reference["document_url"])
        document_text = reference["document_text"]
        st.markdown(
            f"**{reference_index}.** [{document_url}]({document_url})")
        markdown_content = re.sub(
            r"<b>(.*?)</b>", r"**\1**", document_text, flags=re.IGNORECASE)

        with stylable_container(
          key=f"ref_{reference_index}",
          css_styles=REFERENCE_CSS_STYLE
        ):
          st.markdown(markdown_content)

        reference_index = reference_index + 1
      st.divider()

  if "plan" in item:
    with st.chat_message("ai"):
      plan_index = 1

      plan = get_plan(item["plan"]["id"])
      logging.info(plan)

      for step in plan["plan_steps"]:
        st.text_area(f"step-{item_index}", step["description"],
                      height=30, disabled=True,
                      label_visibility="hidden")
        plan_index += 1

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

  agent_logs = item.get("agent_logs", None)
  if agent_logs and agent_logs.strip() != "":
    with st.expander("Expand to see Agent's thought process"):
      st.write(format_ai_output(agent_logs))

  item_index += 1

def reset_content():
  global content_container
  global messages_container
  with content_container:
    st.write("Reloading...")


def chat_page():
  global content_container
  global messages_container
  global spinner_container
  global on_submit_clicked

  chat_theme()

  # display chat header
  chat_header(refresh_func=reset_content)

  st.title("Chat")
  chat_metadata()

  # List all existing chats if any. (data model: UserChat)
  chat_history_panel()

  content_container = st.empty()
  spinner_container = st.empty()

  with content_container:
    messages_container = st.container()

  with messages_container:
    init_messages()

    # Pass prompt from the Landing page if any.
    landing_user_input = st.session_state.get("landing_user_input", None)
    logging.info("Landing input [%s]", landing_user_input)

    if not st.session_state.chat_id and landing_user_input:
      user_input = st.session_state.landing_user_input
      st.session_state.user_input = user_input
      st.session_state.landing_user_input = None
      on_submit(user_input)

    with st.form("user_input_form", border=False, clear_on_submit=True):
      input_col, button_col = st.columns([9.4, .6])

      with input_col:
        user_input = st.text_input(
          placeholder="Enter a prompt here",
          label="Enter prompt",
          label_visibility="collapsed",
          key="user_input"
        )
      with button_col:
        on_submit_clicked = st.form_submit_button("Submit")

    if on_submit_clicked:
      on_submit(user_input)


if __name__ == "__main__":
  utils.init_page()
  chat_page()
