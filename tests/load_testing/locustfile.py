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
import random
import time

from locust import HttpUser, task, events
from locust.runners import MasterRunner, WorkerRunner
from config import BASE_URL
from user_data import users

runner = None
total_response_size = 0
response_count = 0
print_counter = 0

def my_request_handler(request_type, name, response_time, response_length, response, context, exception, **kwargs):
  """
  A custom event handler to log successful requests and their response sizes.
  """
  global total_response_size, response_count, print_counter
  if exception is None:
    if not isinstance(runner, (MasterRunner, WorkerRunner)):
      total_response_size += response_length
      response_count += 1
      print_counter +=1

      if print_counter >= 1000:
        avg_response_size = total_response_size / response_count
        print(
            f"Request succeeded: {request_type} {name}, Response time: {response_time}, Response size: {response_length}"
        )
        print(
            f"total_response_size: {total_response_size}, response_count: {response_count}, avg_response_size: {avg_response_size}"
        )
        print_counter = 0

events.request.add_listener(my_request_handler)

user_creds = users.copy()

class GetChatTypesUser(HttpUser):
  """Performs a basic get request to verify load testing"""
  def on_start(self):
    global runner
    runner = self.environment.runner
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
        f"Insufficient user credentials provided, only {len(users)} found")

  @task
  def get_chat_types(self):
    sleep_time = random.random()
    time.sleep(sleep_time * 10.0 + 1)
    chat_types_url = f"{BASE_URL}/llm-service/api/v1/chat/chat_types"
    self.client.get(chat_types_url, headers=self.headers, timeout=10)

  @task
  def create_chat_and_ask_question(self):
    chat_id = None
    create_chat_resp = None
    create_chat_url = f"{BASE_URL}/llm-service/api/v1/chat/empty_chat"
    try:
      sleep_time = random.random()
      time.sleep(sleep_time * 20.0 + 5)
      create_chat_resp = self.client.post(
        create_chat_url, timeout=10,
        headers=self.headers)
      chat_id = create_chat_resp.json()["data"]["id"]
    except Exception as ex:
      print(ex)
      print(create_chat_resp.text)
      return

    continue_chat_url = f"{BASE_URL}/llm-service/api/v1/chat/{chat_id}/generate"
    # using a common name allows locust to group together api calls with
    # path parameters
    common_name = f"{BASE_URL}/llm-service/api/v1/chat/<chat_id>/generate"
    # Sample questions
    questions = [
        "Name the continents and oceans",
        "What is the capital of France? What other countries does France border",
        "Explain the theory of relativity.",
        "List the planets in our solar system, order them by number of moons",
        "What are the primary colors? How are they different from rainbow colors",
        "Describe the process of photosynthesis.",
        "Who wrote Hamlet? List two other novels that he wrote.",
        "What is the highest mountain on each of the continents?",
        "Explain the concept of artificial intelligence.",
        "What are the major causes of climate change?"
    ]
    req_body = {"prompt": random.choice(questions), "llm_type": "VertexAI-Chat"}
    self.client.post(continue_chat_url, headers=self.headers,
                     timeout=10, json=req_body, name=common_name)


