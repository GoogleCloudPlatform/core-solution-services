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
from common.utils.request_handler import get_method, post_method
from common.models import Agent, UserChat
from config import auth_client, API_BASE_URL
from typing import List
import streamlit as st
import requests

LLM_SERVICE_URL = API_BASE_URL.rstrip("/") + "/llm-service/api/v1"
AUTH_API_URL = API_BASE_URL.rstrip("/") + "/authentication/api/v1"

def get_auth_token():
  return st.session_state.get("auth_token", None)

def handle_error(response):
  if response.status_code != 200:
    raise RuntimeError(f"Error with status {response.status_code}: {str(response)}")

def get_agents() -> List[Agent]:
  """
  Return list of Agent models from LLM Service
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_URL}/agent"
  resp = get_method(api_url,
                    auth_token=None)
  json_response = resp.json()

  # load agent models based on response
  agent_list = []
  for agent_name in json_response.get("data"):
    agent_list.append(Agent.get_by_name(agent_name))
  return agent_list

def run_agent(agent_name: str, prompt: str,
              chat_id: str=None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  if chat_id:
    api_url = f"{LLM_SERVICE_URL}/agent/run/{agent_name}/{chat_id}"
  else:
    api_url = f"{LLM_SERVICE_URL}/agent/run/{agent_name}"
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

def get_all_chats(skip=0, limit=20, auth_token=None) -> List[UserChat]:
  """
  Retrieve all chats of a specific user.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_URL}/chat?skip={skip}&limit={limit}"
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

  api_url = f"{LLM_SERVICE_URL}/chat/{chat_id}"
  resp = get_method(api_url,
                    token=auth_token)
  json_response = resp.json()
  output = json_response["data"]
  return output

def login_user(user_email, user_password, base_url=None) -> str:
    req_body = {
        "email": user_email,
        "password": user_password
    }
    url = f"{AUTH_API_URL}/sign-in/credentials"
    sign_in_req = requests.post(url, json=req_body, verify=False)

    sign_in_res = sign_in_req.json()
    if sign_in_res is None or sign_in_res["data"] is None:
        print("User signed in fail", sign_in_req.text)
    else:
        print(f"Signed in with existing user '{user_email}'. ID Token:\n")
        id_token = sign_in_res["data"]["idToken"]
        st.session_state['loggedIn'] = True
        st.session_state['is_authenticated'] = True 
        return id_token
