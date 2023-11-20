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
  Unit tests for LLM Service agent planning endpoints
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,unused-import,unused-variable,ungrouped-imports
import os
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest import mock
from schemas.schema_examples import (LLM_GENERATE_EXAMPLE, CHAT_EXAMPLE,
                                     USER_EXAMPLE, USER_PLAN_EXAMPLE,
                                     USER_PLAN_STEPS_EXAMPLE_1,
                                     USER_PLAN_STEPS_EXAMPLE_2)
from testing.test_config import API_URL
from common.models.llm import CHAT_HUMAN, CHAT_AI
from common.models import UserChat, User, UserPlan, PlanStep
from common.utils.http_exceptions import add_exception_handlers
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from services.agents.agent_service import get_all_agents

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["PROJECT_ID"] = "fake-project"
os.environ["OPENAI_API_KEY"] = "fake-key"
os.environ["COHERE_API_KEY"] = "fake-key"


FAKE_AGENT_RUN_PARAMS = {
    "llm_type": "VertexAI-Chat",
    "prompt": "test prompt"
  }

FAKE_GENERATE_RESPONSE = "test generation"


# assigning url
api_url = f"{API_URL}/agent/plan"

with mock.patch("google.cloud.secretmanager.SecretManagerServiceClient"):
  from routes.agent import router
  from common.testing.client_with_emulator import client_with_emulator

app = FastAPI()
add_exception_handlers(app)
app.include_router(router, prefix="/llm-service/api/v1")


@pytest.fixture
def create_user(clean_firestore):
  user_dict = USER_EXAMPLE
  user = User.from_dict(user_dict)
  user.save()

@pytest.fixture
def create_chat(clean_firestore):
  chat_dict = CHAT_EXAMPLE
  chat = UserChat.from_dict(chat_dict)
  chat.save()

@pytest.fixture
def create_plan(clean_firestore):
  plan_dict = USER_PLAN_EXAMPLE
  plan = UserPlan.from_dict(plan_dict)
  plan.save()
  plan_step = PlanStep.from_dict(USER_PLAN_STEPS_EXAMPLE_1)
  plan_step.save()
  plan_step = PlanStep.from_dict(USER_PLAN_STEPS_EXAMPLE_2)
  plan_step.save()
  return plan


def test_get_user_plan(create_plan, client_with_emulator):
  url = f"{api_url}/{create_plan.id}"
  resp = client_with_emulator.get(url)
  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"


def test_agent_plan(create_user, create_plan, client_with_emulator):
  url = f"{api_url}/Task"

  with mock.patch("routes.agent_plan.agent_plan",
                  return_value = (FAKE_GENERATE_RESPONSE, create_plan)):
    resp = client_with_emulator.post(url, json=FAKE_AGENT_RUN_PARAMS)

  json_response = resp.json()
  assert resp.status_code == 200, "Status 200"
  response_data = json_response.get("data")
  assert response_data["content"] == FAKE_GENERATE_RESPONSE, "agent output"

