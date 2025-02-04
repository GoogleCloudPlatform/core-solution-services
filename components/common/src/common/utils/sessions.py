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

"""
student learner profile integration service
"""
import datetime
from common.models.session_sql import Session
from common.utils.http_exceptions import InternalServerError

# pylint: disable = protected-access, redefined-outer-name

def create_session(user_id: str = None):
  """ Create a new session"""
  try:
    new_session = Session()
    new_session.user_id = user_id
    new_session.session_id = ""
    new_session.save()  # Save to generate the ID
    print("ID:", new_session.id)
    print("Session ID:", new_session.session_id)
    new_session.session_id = new_session.id  # Now assign the session_id
    new_session.session_desc = "123"
    new_session.update()
    return new_session.get_fields(reformat_datetime=True)
  except Exception as e:
    raise InternalServerError(str(e)) from e

if __name__ == "__main__":
  from common.testing.example_objects import TEST_SESSION
  new_session = create_session(TEST_SESSION["user_id"])
  session = Session.find_by_id(new_session["id"])
  assert session.user_id == TEST_SESSION["user_id"]
  assert session.session_id == session.id
