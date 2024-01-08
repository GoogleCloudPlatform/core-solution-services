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
  Unit tests for association endpoints
"""
import os
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-import,unused-argument,redefined-outer-name
from fastapi import FastAPI
from fastapi.testclient import TestClient
from routes.association_group import router
from testing.test_config import API_URL
from schemas.schema_examples import (BASIC_ASSOCIATION_GROUP_EXAMPLE,
                                     ASSOCIATION_GROUP_EXAMPLE,
                                     BASIC_USER_MODEL_EXAMPLE
                                     )
from common.models import AssociationGroup, User
from common.testing.firestore_emulator import (firestore_emulator,
                                               clean_firestore)
from common.utils.http_exceptions import add_exception_handlers

app = FastAPI()
add_exception_handlers(app)
app.include_router(router, prefix="/user-management/api/v1")

client_with_emulator = TestClient(app)

# assigning url
api_url = f"{API_URL}/association-groups"

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"

def test_search_association_group(clean_firestore):
  association_group_dict = {**BASIC_ASSOCIATION_GROUP_EXAMPLE}
  association_group_dict["association_type"] = "discipline"
  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  params = {"search_query": association_group.name}

  url = f"{api_url}/search"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()

  assert resp.status_code == 200, "Status not 200"
  assert json_response["data"][0][
          "name"] == association_group.name, "Response not received"

def test_search_association_group_negative1(clean_firestore):
  association_group_dict = {**BASIC_ASSOCIATION_GROUP_EXAMPLE}
  association_group_dict["association_type"] = "discipline"
  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  params = {"search_query": association_group.name,  "skip":0, "limit":0}

  url = f"{api_url}/search"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()

  assert resp.status_code == 422, "Status not 422"
  assert json_response.get("success") is False, "Response is not False"

def test_search_association_group_negative2(clean_firestore):
  association_group_dict = {**BASIC_ASSOCIATION_GROUP_EXAMPLE}
  association_group_dict["association_type"] = "discipline"
  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  params = {"search_query": ""}

  url = f"{api_url}/search"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()

  assert resp.status_code == 422, "Status not 422"
  assert json_response.get("success") is False, "Response is not False"
  assert json_response.get("message") == "search_query cannot be empty"

def test_association_group(clean_firestore):
  association_group_dict = {**ASSOCIATION_GROUP_EXAMPLE}
  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  params = {"skip": 0, "limit": 3 }

  url = f"{api_url}"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()

  assert resp.status_code == 200, "Status should be 200"
  retrieved_ids = [i.get("uuid") for i in json_response.get("data")]
  assert association_group.uuid in retrieved_ids, "Response received"

def test_association_group_with_negative_filter(clean_firestore):
  association_group_dict = {**ASSOCIATION_GROUP_EXAMPLE}
  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  params = {"skip": 0, "limit": -3 }

  url = f"{api_url}"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()

  assert resp.status_code == 422, "Status should be 422"
  assert json_response.get(
      "message"
  ) == "Validation Failed"

def test_association_group_with_association_type_filter(clean_firestore):
  association_group_dict = {**ASSOCIATION_GROUP_EXAMPLE}
  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  params = {"skip": 0, "limit": 1, "association_type": "discipline" }

  url = f"{api_url}"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()

  assert resp.status_code == 200, "Status should be 200"
  retrieved_association_type =[i.get("association_type")
    for i in json_response.get("data")]
  assert association_group.association_type in retrieved_association_type
  retrieved_ids = [i.get("uuid") for i in json_response.get("data")]
  assert association_group.uuid in retrieved_ids, "Response received"


def test_get_users_by_usertype(clean_firestore):
  #create user
  user_dict = {**BASIC_USER_MODEL_EXAMPLE}
  user_dict["user_type"] = "coach"
  user_dict["user_type_ref"] = ""
  user = User.from_dict(user_dict)
  user.user_id = ""
  user.save()
  user.user_id = user.id
  user.update()
  user_dict["user_id"] = user.id

  #create association group
  association_group_dict = {**BASIC_ASSOCIATION_GROUP_EXAMPLE,
                            "association_type": "learner",
                            "associations": {"coaches": [],
                                      "instructors": [],
                                      "curriculum_pathway_id": ""}}
  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  params = {"user_type": "coach"}

  url = f"{api_url}/{association_group.uuid}/addable-users"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()
  assert resp.status_code == 200, "Status should be 200"

  assert json_response.get("data")[0]["user_id"
                ] == user.id, "expected data not retrieved"

def test_get_users_by_usertype_for_learner(clean_firestore):
  "when the user of type learner present in an assocation group"
  #create user
  user_dict = {**BASIC_USER_MODEL_EXAMPLE}
  user_dict["user_type"] = "learner"
  user_dict["user_type_ref"] = ""
  user = User.from_dict(user_dict)
  user.user_id = ""
  user.save()
  user.user_id = user.id
  user.update()
  user_dict["user_id"] = user.id

  #association_group with above user_id
  association_group_dict = {**BASIC_ASSOCIATION_GROUP_EXAMPLE,
                            "association_type": "learner",
                            "users": [{
                                "user": user.id,
                                "status": "active",
                                "user_group_type": "learner"
                                }]
                            }

  association_group = AssociationGroup.from_dict(association_group_dict)
  association_group.uuid = ""
  association_group.save()
  association_group.uuid = association_group.id
  association_group.update()

  #association_group that users will be added to
  association_group_dict1 = {**BASIC_ASSOCIATION_GROUP_EXAMPLE,
                            "association_type": "learner"}
  association_group1 = AssociationGroup.from_dict(association_group_dict1)
  association_group1.uuid = ""
  association_group1.save()
  association_group1.uuid = association_group1.id
  association_group1.update()

  params = {"user_type": "learner"}

  url = f"{api_url}/{association_group1.uuid}/addable-users"
  resp = client_with_emulator.get(url, params=params)
  json_response = resp.json()
  assert resp.status_code == 200, "Status should be 200"
  assert json_response.get("data"
                      ) == [], "expected data not retrieved"
