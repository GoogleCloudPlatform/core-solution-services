# Copyright 2023 Google LLC
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
API interface for streamlit UX
"""
# pylint: disable=unused-import,unused-argument
import requests
from typing import List
import streamlit as st

from common.utils.request_handler import get_method, post_method
from common.models import Agent, UserChat, UserPlan
from common.config import API_BASE_URL


LLM_SERVICE_PATH = "llm-service/api/v1"
AUTH_SERVICE_PATH = "authentication/api/v1"

def get_auth_token():
  return st.session_state.get("auth_token", None)

def get_api_base_url():
  api_base_url = st.session_state.get("api_base_url", API_BASE_URL)
  print(f"api_base_url = {api_base_url}")
  return api_base_url.rstrip("/")

def handle_error(response):
  if response.status_code != 200:
    raise RuntimeError(
      f"Error with status {response.status_code}: {str(response)}")

def get_agents(auth_token=None) -> List[Agent]:
  """
  Return list of Agent models from LLM Service
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  api_url = f"{api_base_url}/{LLM_SERVICE_PATH}/agent"
  resp = get_method(api_url, auth_token)
  json_response = resp.json()

  # load agent models based on response
  agent_list = []
  for agent_name in json_response.get("data"):
    agent_list.append(Agent.find_by_name(agent_name))
  return agent_list

def run_agent(agent_name: str, prompt: str,
              chat_id: str = None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  if chat_id:
    api_url = f"""{api_base_url}/{LLM_SERVICE_PATH}
    /agent/run/{agent_name}/{chat_id}"""
  else:
    api_url = f"{api_base_url}/{LLM_SERVICE_PATH}/agent/run/{agent_name}"
  request_body = {
    "prompt": prompt
  }

  print(api_url)
  resp = post_method(api_url,
                     request_body=request_body,
                     token=auth_token)
  handle_error(resp)
  json_response = resp.json()

  print(json_response)
  output = json_response["data"]
  return output

def run_agent_plan(agent_name: str, prompt: str,
                   chat_id: str = None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  if chat_id:
    api_url = f"""{api_base_url}/{LLM_SERVICE_PATH}
    /agent/plan/{agent_name}/{chat_id}"""
  else:
    api_url = f"""{api_base_url}/{LLM_SERVICE_PATH}
    /agent/plan/{agent_name}"""
  request_body = {
    "prompt": prompt
  }

  print(api_url)
  resp = post_method(api_url,
                     request_body=request_body,
                     token=auth_token)
  handle_error(resp)
  json_response = resp.json()

  print(json_response)
  output = json_response["data"]
  return output


def run_agent_execute_plan(plan_id: str,
                           auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  api_url = f"{api_base_url}/{LLM_SERVICE_PATH}/agent/plan/" \
            f"{plan_id}/run"

  print(api_url)
  resp = post_method(api_url,
                     token=auth_token)
  handle_error(resp)
  json_response = resp.json()

  print(json_response)
  output = json_response["data"]
  return output


def run_query(query_engine_id: str, prompt: str,
              chat_id: str = None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  print(chat_id)
  api_base_url = get_api_base_url()
  api_url = f"{api_base_url}/{LLM_SERVICE_PATH}/query/engine/{query_engine_id}"
  request_body = {
    "prompt": prompt,
    "llm_type": "VertexAI-Chat"
  }

  print(api_url)
  resp = post_method(api_url,
                     request_body=request_body,
                     token=auth_token)
  handle_error(resp)
  json_response = resp.json()

  print(json_response)
  output = json_response["data"]
  return output

def get_all_query_engines(auth_token=None):
  """
  Retrieve all chats of a specific user.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  api_url = f"{api_base_url}/{LLM_SERVICE_PATH}/query"
  resp = get_method(api_url,
                    token=auth_token)
  json_response = resp.json()
  print(resp)

  print(json_response)

  output = json_response["data"]
  return output

def get_all_chats(skip=0, limit=20, auth_token=None,
                   with_first_history=True) -> List[UserChat]:
  """
  Retrieve all chats of a specific user.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  api_url = f"""{api_base_url}/{LLM_SERVICE_PATH}/chat?skip={skip}
            &limit={limit}&with_first_history={with_first_history}"""
  print(api_url)

  resp = get_method(api_url,
                    token=auth_token)
  json_response = resp.json()
  output = json_response["data"]
  return output

def get_chat(chat_id, auth_token=None) -> UserChat:
  """
  Retrieve a specific UserChat object
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  api_url = f"{api_base_url}/{LLM_SERVICE_PATH}/chat/{chat_id}"
  resp = get_method(api_url,
                    token=auth_token)
  json_response = resp.json()
  output = json_response["data"]
  return output

def get_plan(plan_id, auth_token=None) -> UserPlan:
  """
  Retrieve a specific UserPlan object
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_base_url = get_api_base_url()
  api_url = f"{api_base_url}/{LLM_SERVICE_PATH}/agent/plan/" \
            f"{plan_id}"
  resp = get_method(api_url,
                    token=auth_token)
  json_response = resp.json()
  output = json_response["data"]
  return output


def login_user(user_email, user_password) -> str or None:
  req_body = {
    "email": user_email,
    "password": user_password
  }
  api_base_url = get_api_base_url()
  url = f"{api_base_url}/{AUTH_SERVICE_PATH}/sign-in/credentials"
  print(f"API url: {url}")

  sign_in_req = requests.post(url, json=req_body, verify=False, timeout=10)

  sign_in_res = sign_in_req.json()
  if sign_in_res is None or sign_in_res["data"] is None:
    print("User signed in fail", sign_in_req.text)
    return None

  else:
    print(f"Signed in with existing user '{user_email}'. ID Token:\n")
    id_token = sign_in_res["data"]["idToken"]
    st.session_state["logged_in"] = True
    st.session_state["auth_token"] = id_token
    return id_token
