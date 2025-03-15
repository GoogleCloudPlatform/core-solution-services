"""
Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import requests
import uuid
from locust import HttpUser, task
from config import USERNAME, PASSWORD, BASE_URL

def get_token(user_email: str, user_password: str, base_url: str) -> str:
  req_body = {
    "email": user_email,
    "password": user_password
  }
  credentails_url = f"{base_url}/authentication/api/v1/sign-in/credentials"
  sign_in_req = requests.post(credentails_url, json=req_body, verify=False,
                              timeout=10)
  sign_in_res = sign_in_req.json()
  id_token = sign_in_res["data"]["idToken"]
  return id_token

# getting an initail token to be shared between all users
# all requests are from a single user, future work can add support for requests
# coming from unique users
INITIAL_ID_TOKEN = get_token(USERNAME, PASSWORD, BASE_URL)

class GetChatTypesUser(HttpUser):
  """Performs a basic get request to verify load testing"""
  def on_start(self):
    self.headers = {"Authorization": f"Bearer {INITIAL_ID_TOKEN}"}

  @task
  def get_chat_types(self):
    chat_types_url = f"{BASE_URL}/llm-service/api/v1/chat/chat_types"
    self.client.get(chat_types_url, headers=self.headers, timeout=10)

  @task
  def create_chat_and_ask_question(self):
    create_chat_url = f"{BASE_URL}/llm-service/api/v1/chat/empty_chat"
    create_chat_resp = self.client.post(
      create_chat_url, timeout=10,
      headers=self.headers)
    chat_id = create_chat_resp.json()["data"]["id"]
    continue_chat_url = f"{BASE_URL}/llm-service/api/v1/chat/{chat_id}/generate"
    # using a common name allows locust to group together api calls with
    # path parameters
    common_name = f"{BASE_URL}/llm-service/api/v1/chat/<chat_id>/generate"
    req_body = {"prompt": "Name the continents", "llm_type": "VertexAI-Chat"}
    self.client.post(continue_chat_url, headers=self.headers,
                     timeout=10, json=req_body, name=common_name)


