"""
Copyright 2023 Google LLC

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

import subprocess
import re
import requests
import argparse
import getpass

from common.models import User

AUTH_API_PATH = "/authentication/api/v1"

USER_DATA = {
    "first_name": "test",
    "last_name": "test",
    "status": "active",
    "user_type": "user",
    "user_groups": [],
    "is_registered": True,
    "failed_login_attempts_count": 0,
    "access_api_docs": True,
    "gaia_id": "fake-gaia-id",
}
requests.packages.urllib3.disable_warnings()

def execute_command(command):
  output = subprocess.check_output(command,
                                   shell=True,
                                   text=True)
  return output.strip()


def create_user(user_email, user_password, base_url=None) -> None:
  """
  Function to do firebase login
  """
  input_user = {**USER_DATA, "email": user_email}
  user = User.from_dict(input_user)
  user.user_id = ""
  user.user_type_ref = ""
  user.save()
  user.user_id = user.id
  user.update()

  req_body = {
    "email": user_email,
    "password": user_password
  }
  url = f"{base_url}/{AUTH_API_PATH}/sign-up/credentials"
  url = re.sub(r"(?<!:)\/+", "/", url)
  sign_up_req = requests.post(url, json=req_body, verify=False)
  sign_up_res = sign_up_req.json()

  # If returns 200, the user was created successfully. Print the token then.
  if sign_up_req.status_code == 200:
    print(f"User '{user_email}' created successfully. ID Token:\n")
    print(sign_up_res["data"]["idToken"])
    print()

  # If the user already exists, sign in the user and get the token.
  elif sign_up_req.status_code == 422 and sign_up_res.get(
    "message") == "EMAIL_EXISTS":
    print(f"User with {user_email} already exists. Trying log in")
    login_user(user_email, user_password, base_url=base_url)

  else:
    print(f"Sign up error. Status: {sign_up_req.status_code}")
    print(sign_up_res)

def login_user(user_email, user_password, base_url=None) -> None:
  req_body = {
    "email": user_email,
    "password": user_password
  }
  url = f"{base_url}/{AUTH_API_PATH}/sign-in/credentials"
  url = re.sub(r"(?<!:)\/+", "/", url)
  sign_in_req = requests.post(url, json=req_body, verify=False)

  sign_in_res = sign_in_req.json()
  if sign_in_res is None or sign_in_res["data"] is None:
    print("User signed in fail", sign_in_req.text)
    raise Exception("User sign-in failed")

  print(f"Signed in with existing user '{user_email}'. ID Token:\n")
  print(sign_in_res["data"]["idToken"])
  print()


def create_admin(base_url="http://authentication") -> None:
  user_email = execute_command(
    "gcloud config list account --format 'value(core.account)' | head -n 1")
  print(f"User email: {user_email}")
  user_password = getpass.getpass(prompt="Password (At least 6 alphanumeric): ")
  confirm_password = getpass.getpass(prompt="Confirm password: ")
  assert user_password == confirm_password, "Passwords don't match."

  print()
  create_user(user_email, user_password, base_url=base_url)


def get_token(base_url="http://authentication"):
  user_email = input("User email: ")
  user_password = getpass.getpass(prompt="Password: ")
  print()
  login_user(user_email, user_password, base_url=base_url)


def main():
  parser = argparse.ArgumentParser()
  parser.add_argument("action", type=str, help="Main action")
  parser.add_argument("--base-url", type=str, help="API base URL")
  args = parser.parse_args()

  if not args.base_url:
    base_url = input("Provide API base URL (e.g.  http://127.0.0.1/): ")
  else:
    base_url = args.base_url
    print(f"API base URL: {base_url}")
  assert base_url, "base_url is empty."

  if args.action == "create_admin":
    create_admin(base_url=base_url)

  elif args.action == "create_user":
    user_email = input("User email: ")
    user_password = getpass.getpass(prompt="Password: ")
    create_user(user_email, user_password, base_url=base_url)

  elif args.action == "get_token":
    get_token(base_url=base_url)

  else:
    print(f"Action {args.action} not supported. Available actions:")
    available_actions = ["create_admin"]
    for action in available_actions:
      print(f" - {action}")

if __name__ == "__main__":
  main()
