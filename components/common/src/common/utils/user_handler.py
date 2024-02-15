# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Helper functions to handle user related operations."""
from common.models import User
from common.utils.logging_handler import Logger
# pylint: disable=logging-fstring-interpolation

Logger = Logger.get_logger(__file__)

DEFAULT_USER_FIRSTNAME = "Test"
DEFAULT_USER_LASTNAME = "Test"
DEFAULT_USER_TYPE = "user"

def get_user_by_email(email,
                      check_firestore_user=False,
                      create_if_not_exist=False):
  Logger.info(f"Find user {email}")
  user = User.find_by_email(email)

  if check_firestore_user and not user:
    if create_if_not_exist:
      return create_user_in_firestore({
        "user_id": email,
        "email": email,
      })

    Logger.error(f"user {email} not found in the database")
    raise ValueError(f"Unauthorized: user {email} not found in the database.")
  return user

def create_user_in_firestore(user_data: dict):
  user = User()
  user.user_id = user_data["user_id"]
  user.email = user_data["email"]
  user.first_name = user_data.get("first_name", DEFAULT_USER_FIRSTNAME)
  user.last_name = user_data.get("last_name", DEFAULT_USER_LASTNAME)
  user.user_type = user_data.get("user_type", DEFAULT_USER_TYPE)
  user.status = "active"
  user.save()
  Logger.info(f"Created user {user.email}")
  return user
