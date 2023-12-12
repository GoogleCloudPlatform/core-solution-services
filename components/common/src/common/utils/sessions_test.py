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
"""
Unit test for session.py
"""
# disabling these rules, as they cause issues with pytest fixtures
# pylint: disable=unused-import,unused-argument,redefined-outer-name
import pytest
from common.models import Session
from common.utils.errors import ResourceNotFoundException
from common.testing.example_objects import TEST_SESSION
from common.testing.firestore_emulator import clean_firestore, firestore_emulator


def test_create_session(firestore_emulator, clean_firestore):
  """test for creating a new session """
  new_session = Section.from_dict(TEST_SESSION)
  new_session.save()
  session = Session.find_by_id(new_session.id)
  assert session.user_id == TEST_SESSION["user_id"]
  assert session.session_id == TEST_SESSION["session_id"]
