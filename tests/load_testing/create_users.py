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
import os
import firebase_admin
from firebase_admin import credentials, auth
import concurrent.futures
import uuid

def create_user(email, password):
  """Creates a single user and returns user data as a dictionary."""
  user = auth.create_user(
    email=email,
    password=password,
  )
  return {"email": email, "password": password, "uid": user.uid}

def create_users(num_users, user_data_file="user_data.py"):
  """Creates users in Firebase Authentication in parallel and saves 
  credentials."""
  if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

  user_data = [(f"{uuid.uuid4()}@example.com", str(uuid.uuid4()))
               for _ in range(num_users)]

  with concurrent.futures.ThreadPoolExecutor() as executor:
    results = executor.map(lambda args: create_user(*args), user_data)
    all_users = list(results)

  with open(user_data_file, "w", encoding="utf-8") as f:
    f.write("users = [\n")
    for user in all_users:
      f.write(f"  {user},\n")
    f.write("]\n")

  for user in all_users:
    if "error" in user:
      print(user["error"])
    else:
      print(f"Successfully created user: {user['uid']}")

def delete_user(uid):
  """Deletes a single user."""
  auth.delete_user(uid)
  return f"Successfully deleted user: {uid}"

def delete_users():
  """Deletes users from Firebase Authentication using the data from the file."""
  if os.path.exists("user_data.py"):
    from user_data import users
  else:
    raise FileNotFoundError("user_data.py not found. Create it using the "
                            "create_users function in this file")
  if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

  with concurrent.futures.ThreadPoolExecutor() as executor:
    results = [executor.submit(delete_user, user["uid"]) for user in users]

    for future in concurrent.futures.as_completed(results):
      print(future.result())
  os.remove("user_data.py")
