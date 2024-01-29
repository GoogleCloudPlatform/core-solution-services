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
  Streamlit app custom Chat Page
"""
# pylint: disable=invalid-name,unused-variable
import re
import streamlit as st
from streamlit_extras.stylable_container import stylable_container
from api import (
    get_chat, run_dispatch, get_plan,
    run_agent_execute_plan, get_all_chat_llm_types, run_agent_plan, run_chat)
from components.chat_options import action_buttons
from components.help_modal import help_form
from styles.pages.custom_chat_markup import custom_chat_theme
from common.utils.logging_handler import Logger
import utils

ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

Logger = Logger.get_logger(__file__)

def on_submit(user_input):
  """ Run dispatch agent when adding an user input prompt """
  # Appending messages.
  st.session_state.error_msg = None
  st.session_state.messages.append({"HumanInput": user_input})

  with st.spinner("Loading..."):
    # Send API to llm-service
    default_route = st.session_state.get("default_route", None)
    if default_route is None or default_route == "Auto":
      response = run_dispatch(user_input,
                              chat_id=st.session_state.get("chat_id"),
                              llm_type=st.session_state.get("chat_llm_type"))
      st.session_state.default_route = response.get("route", None)
    elif default_route == "Chat":
      response = run_chat(user_input,
                         chat_id=st.session_state.get("chat_id"),
                         llm_type=st.session_state.get("chat_llm_type"))
    elif default_route == "Plan":
      response = run_agent_plan("Plan", user_input,
                                chat_id=st.session_state.get("chat_id"),
                                llm_type=st.session_state.get("chat_llm_type"))
    else:
      st.error(f"Unsupported route {default_route}")

    st.session_state.chat_id = response["chat"]["id"]

    # TODO: Currently the AIOutput vs content are inconsistent across
    # API response and in a UserChat history.
    if "content" in response:
      response["AIOutput"] = response["content"]
    del response["chat"]

    st.session_state.messages.append(response)

  # reload page after exiting from spinner
  utils.navigate_to("Custom_Chat")


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

def chat_content():
  if st.session_state.debug:
    with st.expander("DEBUG: session_state"):
      st.write(st.session_state.get("landing_user_input"))
      st.write(st.session_state.get("messages"))

  # Create a placeholder for all chat history.
  chat_placeholder = st.empty()
  with chat_placeholder.container():
    index = 1
    has_input = False
    needs_help = False
    for item in st.session_state.messages:
      Logger.info(item)

      if "HumanInput" in item:
        has_input = True
        if item["HumanInput"] == "I need help":
          needs_help = True
        with st.chat_message("user"):
          st.write(item["HumanInput"], is_user=True, key=f"human_{index}")

      if "AIOutput" in item:
        if needs_help:
          if "help_state" not in st.session_state:
            st.session_state.help_state = False

          if st.session_state.help_state is False:
            with st.chat_message("ai"):
              st.write(
                  "If it's an emergency, please dial 911. Otherwise, complete the form below",
                  key=f"em_{index}"
              )
            with st.expander("Get Further Assistance", expanded=True):
              help_form()
          else:
            with st.chat_message("ai"):
              st.markdown(
                  "Your ticket number is: **5010**<br>"\
                  "You will receive an **email notification** within 48 hours.<br>"\
                  "You may continue to utilize the chat assistant, or can close or "\
                  "navigate away from this window.",
                  unsafe_allow_html=True
              )

          needs_help = False
        else:
          with st.chat_message("ai"):
            ai_output = item["AIOutput"]
            ai_output = format_ai_output(ai_output)
            st.write(
                ai_output,
                key=f"ai_{index}",
                unsafe_allow_html=False,
                is_table=False,  # TODO: Detect whether an output content type.
            )

      route_logs = item.get("route_logs", None)
      if route_logs and route_logs.strip() != "":
        with st.expander("Thought Process"):
          st.write(format_ai_output(route_logs))

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

            #st.text_area(
            #  f"Reference: {document_url}",
            #  document_text,
            #  key=f"ref_{reference_index}")

            with stylable_container(
              key=f"ref_{reference_index}",
              css_styles = """
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
                padding-top: 1rem;
                padding-bottom: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
                background-color: #FFFFFF;
                border: none;
                border-width: 1px;              
                resize: vertical;
                min-height: 95px;
                height: 100px;
              }
              """
            ):
              st.markdown(markdown_content)

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
          if st.button("Execute plan", key=f"plan-{plan_id}"):
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

      index = index + 1

  # Position chat option buttons
  if has_input:
    action_buttons()

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
    st.session_state.messages = [{
      "AIOutput": "You can ask me anything."
    }]


def chat_page():
  custom_chat_theme()

  content_placeholder = st.container()

  # Pass prompt from the Landing page if any.
  landing_user_input = st.session_state.get("landing_user_input", None)
  Logger.info(f"Landing input [{landing_user_input}]")

  if not st.session_state.chat_id and landing_user_input:
    user_input = st.session_state.landing_user_input
    st.session_state.user_input = user_input
    st.session_state.landing_user_input = None
    on_submit(user_input)

  with st.form("user_input_form", border=False, clear_on_submit=True):
    input_col, btn_col = st.columns([9.4, .6])

    with input_col:
      user_input = st.text_input(
        placeholder="Enter a prompt here",
        label="Enter prompt",
        label_visibility="collapsed",
        key="user_input"
      )
    with btn_col:
      submitted = st.form_submit_button("Submit")

    if submitted:
      on_submit(user_input)

  with content_placeholder:
    chat_content()

  ref_col, plan_col, options = st.columns(3)

  with ref_col:
    with st.expander("References", expanded=True):
      url_name = "Medicaid"
      document_url = "https://www.medicaid.gov/"
      document_text = "New York's Medicaid program provides comprehensive health coverage"

      st.write("**Site:**")
      st.markdown(f"[{url_name}]({document_url})")
      st.write("**Overview:**")
      st.write(document_text)

      st.divider()

      st.write("**Site:**")
      st.markdown(f"[{url_name}]({document_url})")
      st.write("**Overview:**")
      st.write(document_text)

  with plan_col:
    for item in st.session_state.messages:
      if "plan" in item:
        plan = get_plan(item["plan"]["id"])
        with st.expander("Plan Steps"):
          for step in plan["plan_steps"]:
            st.write(step["description"])

  with options:
    with st.expander("Advanced Settings"):
      chat_llm_types = get_all_chat_llm_types()
      st.session_state.chat_llm_type = st.selectbox("Model", chat_llm_types)

      st.session_state.default_route = st.selectbox(
        "Chat Mode", ["Auto", "Chat", "Plan", "Query"])


if __name__ == "__main__":
  st.set_page_config(initial_sidebar_state="collapsed")
  utils.init_page()
  init_messages()
  chat_page()
