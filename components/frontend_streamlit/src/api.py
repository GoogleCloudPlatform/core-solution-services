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

from common.utils.logging_handler import Logger
from common.utils.request_handler import get_method, post_method
from common.models import Agent, UserChat, UserPlan
from config import (
    LLM_SERVICE_API_URL, JOBS_SERVICE_API_URL, AUTH_SERVICE_API_URL)

Logger = Logger.get_logger(__file__)

def get_auth_token():
  return st.session_state.get("auth_token", None)

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

  api_url = f"{LLM_SERVICE_API_URL}/agent"
  Logger.info(f"api_url={api_url}")

  resp = get_method(api_url, auth_token)
  Logger.info(resp)
  json_response = resp.json()

  # load agent models based on response
  agent_list = []
  for agent_name in json_response.get("data"):
    agent_list.append(Agent.find_by_name(agent_name))
  return agent_list

def run_dispatch(prompt: str, chat_id: str = None,
                 route=None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/dispatch"
  Logger.info(f"api_url = {api_url}")
  Logger.info(f"chat_id = {chat_id}")

  request_body = {
    "prompt": prompt,
    "chat_id": chat_id,
  }
  resp = post_method(api_url, request_body=request_body, token=auth_token)
  handle_error(resp)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output


def run_agent(agent_name: str, prompt: str,
              chat_id: str = None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/run/{agent_name}"
  if chat_id:
    api_url = api_url + f"/{chat_id}"
  Logger.info(f"api_url={api_url}")

  request_body = {
    "prompt": prompt
  }
  resp = post_method(api_url, request_body=request_body, token=auth_token)
  handle_error(resp)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output

def run_agent_plan(agent_name: str, prompt: str,
                   chat_id: str = None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/plan/{agent_name}"
  if chat_id:
    api_url = api_url + f"/{chat_id}"
  Logger.info(f"api_url={api_url}")

  request_body = {
    "prompt": prompt
  }
  resp = post_method(api_url, request_body=request_body, token=auth_token)
  handle_error(resp)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output


def run_agent_execute_plan(plan_id: str,
                           chat_id: str,
                           auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/plan/" \
            f"{plan_id}/run?chat_id={chat_id}"
  Logger.info(f"api_url={api_url}")

  resp = post_method(api_url, token=auth_token)
  handle_error(resp)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output


def run_query(query_engine_id: str, prompt: str,
              chat_id: str = None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  Logger.info(chat_id)
  api_url = f"{LLM_SERVICE_API_URL}/query/engine/{query_engine_id}"
  Logger.info(f"api_url={api_url}")

  request_body = {
    "prompt": prompt,
    "llm_type": "VertexAI-Chat"
  }
  resp = post_method(api_url, request_body=request_body, token=auth_token)
  handle_error(resp)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output

def build_query_engine(name: str, doc_url: str, embedding_type: str,
                       vector_store: str, description: str,
                       auth_token=None):
  """
  Start a query engine build job
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query/engine"
  Logger.info(f"api_url={api_url}")

  request_body = {
    "query_engine": name,
    "doc_url": doc_url,
    "embedding_type": embedding_type,
    "vector_store": vector_store,
    "description": description,
  }
  resp = post_method(api_url, request_body=request_body, token=auth_token)
  handle_error(resp)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output

def get_all_query_engines(auth_token=None):
  """
  Retrieve all chats of a specific user.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query"
  Logger.info(f"api_url={api_url}")
  resp = get_method(api_url, token=auth_token)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output

def get_all_embedding_types(auth_token=None):
  """
  Retrieve all supported embedding types
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/llm/embedding_types"
  Logger.info(f"api_url={api_url}")
  resp = get_method(api_url, token=auth_token)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output

def get_all_vector_stores(auth_token=None):
  """
  Retrieve all vector store types
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query/vectorstore"
  Logger.info(f"api_url={api_url}")
  resp = get_method(api_url, token=auth_token)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output

def get_all_jobs(job_type="query_engine_build", auth_token=None):
  """
  Retrieve all vector store types
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{JOBS_SERVICE_API_URL}/jobs/{job_type}"
  Logger.info(f"api_url={api_url}")
  resp = get_method(api_url, token=auth_token)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output

def get_all_chats(skip=0, limit=20, auth_token=None,
                   with_first_history=True) -> List[UserChat]:
  """
  Retrieve all chats of a specific user.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"""{LLM_SERVICE_API_URL}/chat?skip={skip}
            &limit={limit}&with_first_history={with_first_history}"""
  Logger.info(f"api_url={api_url}")

  resp = get_method(api_url, token=auth_token)
  Logger.info(resp)
  json_response = resp.json()
  output = json_response["data"]
  return output

def get_chat(chat_id, auth_token=None) -> UserChat:
  """
  Retrieve a specific UserChat object
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/chat/{chat_id}"
  Logger.info(f"api_url={api_url}")

  resp = get_method(api_url, token=auth_token)
  Logger.info(resp)
  json_response = resp.json()
  output = json_response["data"]
  return output

def add_chat_history(chat_id, entry):
  """
  Append a new UserChat history entry.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/chat/{chat_id}"
  Logger.info(f"api_url={api_url}")
  request_body = {
    "chat_id": chat_id,
    "history_entry": entry,
  }
  resp = post_method(api_url, request_body=request_body, token=auth_token)
  handle_error(resp)
  Logger.info(resp)

  json_response = resp.json()
  output = json_response["data"]
  return output


def get_plan(plan_id, auth_token=None) -> UserPlan:
  """
  Retrieve a specific UserPlan object
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/plan/" \
            f"{plan_id}"
  Logger.info(f"api_url={api_url}")

  resp = get_method(api_url, token=auth_token)
  Logger.info(resp)
  json_response = resp.json()
  output = json_response["data"]
  return output


def login_user(user_email, user_password) -> str or None:
  req_body = {
    "email": user_email,
    "password": user_password
  }
  api_url = f"{AUTH_SERVICE_API_URL}/sign-in/credentials"
  Logger.info(f"API url: {api_url}")

  sign_in_req = requests.post(api_url, json=req_body, verify=False, timeout=10)

  sign_in_res = sign_in_req.json()
  if sign_in_res is None or sign_in_res["data"] is None:
    Logger.info("User signed in fail", sign_in_req.text)
    return None

  else:
    Logger.info(f"Signed in with existing user '{user_email}'. ID Token:\n")
    id_token = sign_in_res["data"]["idToken"]
    st.session_state["logged_in"] = True
    st.session_state["auth_token"] = id_token
    return id_token
