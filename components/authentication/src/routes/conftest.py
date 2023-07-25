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

""" conftest.py: Consist of fixtures"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable= unused-import
import pytest
# TODO: Replace TempUser with User once user management is available
from common.models import TempUser
from common.testing.firestore_emulator import (firestore_emulator,
                                               clean_firestore)

BASIC_USER_MODEL_EXAMPLE = {
    "first_name": "jon",
    "last_name": "doe",
    "email": "jon.doe@gmail.com",
    "user_type": "learner",
    "user_type_ref": "U2DDBkl3Ayg0PWudzhI",
    "user_groups": [],
    "status": "active",
    "is_registered": True,
    "failed_login_attempts_count": 0,
    "access_api_docs": False,
    "gaia_id": "F2GGRg5etyty"
}

@pytest.fixture(name="create_user")
def create_user():
  user = TempUser.from_dict(BASIC_USER_MODEL_EXAMPLE)
  user.user_id = ""
  user.save()
  user.user_id = user.id
  user.update()
  return user
