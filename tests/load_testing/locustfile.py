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
from locust import HttpUser, task
from config import BASE_URL
from user_data import users

user_creds = users.copy()

class GetChatTypesUser(HttpUser):
  """Performs a basic get request to verify load testing"""
  def on_start(self):
    if user_creds:
      cur_user = user_creds.pop()
      get_token_url = f"{BASE_URL}/authentication/api/v1/sign-in/credentials"
      creds = {
        "email": cur_user["email"],
        "password": cur_user["password"]
      }
      sign_in_req = self.client.post(get_token_url, json=creds, verify=False,
                              timeout=10)
      sign_in_res = sign_in_req.json()
      token = sign_in_res["data"]["idToken"]
      self.headers = {"Authorization": f"Bearer {token}"}
    else:
      raise ValueError(
        f"Insufficient user credentails provided, only {len(users)} found")

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


