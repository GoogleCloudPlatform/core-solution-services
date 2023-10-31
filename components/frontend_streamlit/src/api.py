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
from config import auth_client, API_URL
from typing import List

def get_agents() -> List[Agent]:
  """
  Return list of Agent models from LLM Service
  """
  api_url = f"{API_URL}/agent"
  resp = get_method(api_url, auth_client=auth_client)
  json_response = resp.json()
  
  # load agent models based on response
  agent_list = []
  for agent_name in json_response.get("data"):
    agent_list.append(Agent.get_by_name(agent_name))
  return agent_list

def run_agent(agent_name: str, prompt: str) -> str:
  """
  Run Agent on human input, and return output
  """
  api_url = f"{API_URL}/agent/run/{agent_name}"
  request_body = {
    "prompt": prompt
  }
  resp = post_method(api_url, request_body=request+body,
                     auth_client=auth_client)
  json_response = resp.json()
  output = json_response["content"]
  return output
