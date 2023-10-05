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

"""Utility method to validate user based on Id Token"""
import re

from fastapi import Request
from common.utils.logging_handler import Logger
from common.utils.errors import InvalidTokenError
from common.utils.auth_service import user_verification


# pylint: disable = consider-using-f-string
def get_user_identity(req: Request) -> dict:
  """
  Get user identity from firebase token
  :param req:
  :return: json/dict
  """
  try:
    token = req.headers["Authorization"]
    res = user_verification(token=token)
    data = res.json()

    if res.status_code == 200:
      if data["success"] is True:
        user_id = data["data"]["user_id"]
        user_email = data["data"]["email"]
        return {"success": True, "user_id": user_id,
                "user_email": user_email, "token":token}
      if data["success"] is False:
        raise InvalidTokenError(data["message"])
    else:
      raise InvalidTokenError(data["message"])
  except InvalidTokenError as e:
    Logger.error("Token error: %s" % e)
    return {
        "success": False,
        "message": re.split(",", e.error)[0],
        "data": None
    }
  except Exception as e: # pylint: disable = broad-except
    Logger.error("Token error: %s" % e)
    return {"success": False, "message": "Internal Server Error", "data": None}
