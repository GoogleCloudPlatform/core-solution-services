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
from common.models import Session
from common.utils.http_exceptions import InternalServerError

def create_session(user_id: str = None):
  """ Create a new session"""
  try:
    new_session = Session()
    data = {"user_id": user_id}
    new_session = new_session.from_dict(data)
    new_session.user_id = user_id
    new_session.session_id = ""
    new_session.save()
    new_session.session_id = new_session.id
    new_session.update()

    return new_session.get_fields(reformat_datetime=True)
  except Exception as e:
    raise InternalServerError(str(e)) from e
