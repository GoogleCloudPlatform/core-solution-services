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
from locust import HttpUser, task


USERNAME = "example@test.com"
PASSWORD = "password"
BASE_URL = "https://my-genie.website.com/"

class GetChatTypesUser(HttpUser):
  """Performs a basic get request to verify load testing"""
  def on_start(self):
    id_token = get_token(USERNAME, PASSWORD, BASE_URL)
    self.headers = {"Authorization": f"Bearer {id_token}"}

  @task
  def get_chat_types(self):
    chat_types_url = f"{BASE_URL}/llm-service/api/v1/chat/chat_types"
    self.client.get(chat_types_url, headers=self.headers, timeout=10)

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
  print(id_token)
  return id_token
