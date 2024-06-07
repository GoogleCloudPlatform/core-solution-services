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
import json
from typing import List
import streamlit as st

import logging
from common.utils.request_handler import (
    get_method, post_method, put_method, delete_method)
from common.models import UserChat, UserPlan
from config import (APP_BASE_PATH, LLM_SERVICE_API_URL,
                    JOBS_SERVICE_API_URL, AUTH_SERVICE_API_URL)


API_TIMEOUT = 600


def dispatch_api(method: str, api_url: str,
                 request_body: dict = None, auth_token: str = None):
  """ dispatch api call based on method """
  if not auth_token:
    auth_token = st.session_state.get("auth_token")

  if method.upper() == "GET":
    resp = get_method(api_url, token=auth_token, timeout=API_TIMEOUT)
  elif method.upper() == "POST":
    resp = post_method(
        api_url, request_body=request_body, token=auth_token,
        timeout=API_TIMEOUT)
  elif method.upper() == "PUT":
    resp = put_method(
        api_url, request_body=request_body, token=auth_token,
        timeout=API_TIMEOUT)
  elif method.upper() == "DELETE":
    resp = delete_method(
        api_url, request_body=request_body, token=auth_token,
        timeout=API_TIMEOUT)
  else:
    raise ValueError(f"method {method} is not supported.")

  resp_dict = get_response_json(resp)
  status_code = resp.status_code
  logging.info("status_code=%s", status_code)

  return resp, resp_dict, status_code


def api_request(method: str, api_url: str,
                request_body: dict = None, auth_token: str = None):
  """ Make API request with error handling. """

  st.session_state.error_msg = None
  try:
    resp = None
    logging.info("api_url=%s, auth_token=%s", api_url, auth_token)

    # global processing of llm_type param
    if request_body and isinstance(request_body, dict):
      llm_type = request_body.get("llm_type", None)
      if llm_type == "default":
        del request_body["llm_type"]

    resp, resp_dict, status_code = dispatch_api(method,
                                                api_url,
                                                request_body,
                                                auth_token)

    if status_code == 401 or resp_dict.get("success", False) is False:
      # refresh token with existing creds and retry on failure to authenticate
      username = st.session_state.get("username", None)
      password = st.session_state.get("password", None)
      logging.info("API responds 401 error. attempting to re-auth with "
                  "username: %s", username)
      if username and password:
        auth_token = login_user(username, password)
        resp, resp_dict, status_code = dispatch_api(method,
                                                    api_url,
                                                    request_body,
                                                    auth_token)

      if status_code == 401:
        logging.error(
            "Unauthorized when calling API: %s", api_url)
        st.session_state.error_msg = \
            "Unauthorized or session expired. " \
            "Please [login]({APP_BASE_PATH}/Login) again."

      if resp_dict.get("success", False) is False:
        msg = resp_dict.get("message", "no message returned")
        st.session_state.error_msg = f"API call failed: {msg} "

    if status_code != 200:
      logging.error("Error with status %s: %s", status_code, str(resp))
      st.session_state.error_msg = \
          f"Error with status {status_code}: {str(resp)}"

    return resp

  except requests.exceptions.ConnectionError as e:
    logging.error(e)
    st.session_state.error_msg = \
        "Unable to connect to backend APIs. Please try again later."

  except RuntimeError as e:
    logging.error(e)
    st.session_state.error_msg = str(e)

  except json.decoder.JSONDecodeError as e:
    logging.error("Unable to parse response: %s", resp)
    logging.error(e)
    st.session_state.error_msg = \
        f"Unable to decode response from backend APIs: {resp}"

  finally:
    if st.session_state.error_msg:
      st.error(st.session_state.error_msg)

      if st.session_state.get("debug", False):
        with st.expander("Expand to see detail:"):
          st.write(f"API URL: {api_url}")
          st.write(e)
      st.stop()


def get_auth_token():
  return st.session_state.get("auth_token", None)


def handle_error(resp):
  if resp.status_code != 200:
    raise RuntimeError(
      f"Error with status {resp.status_code}: {str(resp)}")


def get_response_json(resp):
  try:
    return resp.json()
  except json.decoder.JSONDecodeError as e:
    logging.error("Unable to parse response: %s", resp)
    logging.error(e)
    st.session_state.error_msg = \
        f"Unable to decode response from backend APIs: {resp}"
    return None


def validate_auth_token():
  """
  Validate auth token
  """
  auth_token = get_auth_token()
  api_url = f"{AUTH_SERVICE_API_URL}/validate"
  resp = api_request("GET", api_url, auth_token=auth_token)
  status_code = resp.status_code

  if status_code == 200:
    return True

  return False


def get_agents(auth_token=None) -> List[dict]:
  """
  Return list of Agent models from LLM Service
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent"
  logging.info("api_url=%s", api_url)

  resp = api_request("GET", api_url, auth_token)
  resp_dict = get_response_json(resp)

  agent_config = resp_dict.get("data")
  return agent_config


def get_all_routing_agents(auth_token=None) -> List[dict]:
  """
  Return list of Routing Agent models from LLM Service
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/route"
  logging.info("api_url=%s", api_url)

  resp = api_request("GET", api_url, auth_token)
  resp_dict = get_response_json(resp)

  # load agent models based on response
  agent_config = resp_dict.get("data")
  return agent_config


def run_dispatch(prompt: str, agent_name: str, chat_id: str = None,
                 llm_type: str = None, run_as_batch_job=False,
                 auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/dispatch/{agent_name}"
  logging.info("api_url = %s", api_url)
  logging.info("chat_id = %s", chat_id)

  request_body = {
    "prompt": prompt,
    "chat_id": chat_id,
    "llm_type": llm_type,
    "run_as_batch_job": run_as_batch_job,
  }
  logging.info("request_body: %s", request_body)

  resp = api_request("POST", api_url,
                     request_body=request_body, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)

  logging.info("response: %s", resp_dict)

  return resp_dict["data"]


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
  logging.info("api_url=%s", api_url)

  request_body = {
    "prompt": prompt
  }
  resp = api_request("POST", api_url,
                     request_body=request_body, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def run_agent_plan(agent_name: str, prompt: str,
                   chat_id: str = None, llm_type: str = None,
                   auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/plan/{agent_name}"
  if chat_id:
    api_url = api_url + f"/{chat_id}"
  logging.info("api_url=%s", api_url)

  request_body = {
    "prompt": prompt,
    "llm_type": llm_type
  }
  resp = api_request("POST", api_url,
                     request_body=request_body, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


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
  logging.info("api_url=%s", api_url)

  resp = api_request("POST", api_url, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def run_query(query_engine_id: str, prompt: str,
              chat_id: str = None, llm_type: str = None, auth_token=None):
  """
  Run Agent on human input, and return output
  """
  if not auth_token:
    auth_token = get_auth_token()

  logging.info("chat id = %s", chat_id)
  api_url = f"{LLM_SERVICE_API_URL}/query/engine/{query_engine_id}"
  logging.info("api_url=%s", api_url)

  if llm_type is None:
    llm_type = "VertexAI-Chat"

  request_body = {
    "prompt": prompt,
    "llm_type": llm_type
  }
  resp = api_request("POST", api_url,
                     request_body=request_body, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def run_chat(prompt: str, chat_id: str = None,
             llm_type: str = None, auth_token=None):
  if not auth_token:
    auth_token = get_auth_token()

  logging.info("chat id = %s", chat_id)

  if chat_id:
    api_url = f"{LLM_SERVICE_API_URL}/chat/{chat_id}/generate"
  else:
    api_url = f"{LLM_SERVICE_API_URL}/chat"

  logging.info("api_url=%s", api_url)

  request_body = {
    "prompt": prompt,
    "llm_type": llm_type
  }
  resp = api_request("POST", api_url,
                     request_body=request_body, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def build_query_engine(name: str, engine_type: str, doc_url: str,
                       depth_limit: int, embedding_type: str,
                       vector_store: str, description: str, agents: str,
                       child_engines: str, is_multimodal: str,
                       auth_token=None):
  """
  Start a query engine build job
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query/engine"
  logging.info("api_url=%s", api_url)

  request_body = {
    "query_engine": name,
    "query_engine_type": engine_type,
    "doc_url": doc_url,
    "embedding_type": embedding_type,
    "vector_store": vector_store,
    "description": description,
    "params": {
      "depth_limit": depth_limit,
      "agents": agents,
      "associated_engines": child_engines,
      "is_multimodal": is_multimodal,
    }
  }
  logging.info("Sending request_body=%s to %s", request_body, api_url)
  resp = api_request("POST", api_url,
                     request_body=request_body, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)
  return resp_dict


def update_query_engine(
        query_engine_id: str, name: str, description: str, auth_token=None):
  """
  Update an existing query engine
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query/engine/{query_engine_id}"
  logging.info("api_url=%s", api_url)

  request_body = {
    "query_engine": name,
    "description": description,
    "doc_url": "",
  }
  logging.info("Sending request_body=%s to %s", request_body, api_url)
  resp = api_request("PUT", api_url,
                     request_body=request_body, auth_token=auth_token)
  handle_error(resp)
  resp_dict = get_response_json(resp)
  return resp_dict


def get_all_docs_of_query_engine(query_engine_id, auth_token=None):
  """
  Retrieve all chats of a specific user.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query/urls/{query_engine_id}"
  logging.info("api_url=%s", api_url)
  resp = api_request("GET", api_url, auth_token=auth_token)

  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def get_all_query_engines(auth_token=None) -> List[dict]:
  """
  Retrieve all query engines.  Return a list of dicts containing
  Query Engine model fields.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query"
  logging.info("api_url=%s", api_url)
  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  qe_list = resp_dict["data"]
  if qe_list is None:
    qe_list = []
  return qe_list


def get_all_embedding_types(auth_token=None):
  """
  Retrieve all supported embedding types
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/llm/embedding_types"
  logging.info("api_url=%s", api_url)
  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def get_all_chat_llm_types(auth_token=None):
  """
  Retrieve all supported chat model types
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/chat/chat_types"
  logging.info("api_url=%s", api_url)
  resp = get_method(api_url, token=auth_token)
  logging.info(resp)

  json_response = resp.json()
  output = json_response["data"] or []

  # sort output in reverse order (to put Vertex on top)
  output.sort(reverse=True)

  return output


def get_all_vector_stores(auth_token=None):
  """
  Retrieve all vector store types
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query/vectorstore"
  logging.info("api_url=%s", api_url)
  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def get_all_jobs(job_type="query_engine_build", auth_token=None):
  """
  Retrieve all vector store types
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{JOBS_SERVICE_API_URL}/jobs/{job_type}"
  logging.info("api_url=%s", api_url)
  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)

  output = resp_dict["data"] or []
  output.sort(key=lambda x: x.get("last_modified_time", 0), reverse=True)
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
  logging.info("api_url=%s", api_url)

  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  return resp_dict["data"]


def get_chat(chat_id, auth_token=None) -> UserChat:
  """
  Retrieve a specific UserChat object
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/chat/{chat_id}"
  logging.info("api_url=%s", api_url)

  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  output = resp_dict["data"]
  return output


def delete_chat(chat_id, auth_token=None):
  """
  Delete a specific UserChat object.  We do a hard delete here to be
  developer friendly.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/chat/{chat_id}?hard_delete=True"
  logging.info("api_url=%s", api_url)

  resp = api_request("DELETE", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  output = resp_dict["success"]
  return output


def delete_query_engine(qe_id: str, auth_token=None):
  """
  Delete a specific QueryEngine.  We do a hard delete here to be
  developer friendly.
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/query/engine/{qe_id}?hard_delete=True"
  logging.info("api_url=%s", api_url)

  resp = api_request("DELETE", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  output = resp_dict["success"]
  return output


def get_plan(plan_id, auth_token=None) -> UserPlan:
  """
  Retrieve a specific UserPlan object
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{LLM_SERVICE_API_URL}/agent/plan/" \
            f"{plan_id}"
  logging.info("api_url=%s", api_url)

  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  output = resp_dict["data"]
  return output


def get_job(job_type, job_id, auth_token=None) -> UserChat:
  """
  Retrieve a specific UserChat object
  """
  if not auth_token:
    auth_token = get_auth_token()

  api_url = f"{JOBS_SERVICE_API_URL}/jobs/{job_type}/{job_id}"
  logging.info("api_url=%s", api_url)

  resp = api_request("GET", api_url, auth_token=auth_token)
  resp_dict = get_response_json(resp)
  output = resp_dict["data"]
  return output


def login_user(user_email, user_password) -> str or None:
  req_body = {
    "email": user_email,
    "password": user_password
  }
  api_url = f"{AUTH_SERVICE_API_URL}/sign-in/credentials"
  logging.info("login_user: API url: %s", api_url)

  resp = api_request("POST", api_url, request_body=req_body)
  resp_dict = get_response_json(resp)
  if resp_dict is None or resp_dict["data"] is None:
    logging.info("User signed in fail: %s", resp_dict.text)
    st.session_state["logged_in"] = False
    st.session_state["auth_token"] = None
    st.error("Invalid username or password")
    return None

  else:
    id_token = resp_dict["data"]["idToken"]
    st.session_state["logged_in"] = True
    st.session_state["auth_token"] = id_token
    st.session_state["username"] = user_email
    st.session_state["password"] = user_password
    logging.info(
        "Signed in with existing user '%s'. ID Token:\n%s",
        user_email, id_token)
    return id_token
