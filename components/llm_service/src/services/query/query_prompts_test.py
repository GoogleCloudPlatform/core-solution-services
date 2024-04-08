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
  Unit tests for Query Prompts
"""
# pylint: disable=unused-argument,redefined-outer-name,unused-import
import pytest
from services.query.query_prompts import get_question_prompt
from services.query.query_prompt_config import QUESTION_PROMPT
from common.models import QueryReference
from common.testing.firestore_emulator import firestore_emulator, clean_firestore
from schemas.schema_examples import (QUERY_REFERENCE_EXAMPLE_1,
                                     QUERY_REFERENCE_EXAMPLE_2)

@pytest.fixture
def create_query_reference(firestore_emulator, clean_firestore):
  query_reference_dict = QUERY_REFERENCE_EXAMPLE_1
  query_reference = QueryReference.from_dict(query_reference_dict)
  query_reference.save()
  return query_reference

@pytest.fixture
def create_query_reference_2(firestore_emulator, clean_firestore):
  query_reference_dict = QUERY_REFERENCE_EXAMPLE_2
  query_reference = QueryReference.from_dict(query_reference_dict)
  query_reference.save()
  return query_reference

def test_question_prompt(create_query_reference, create_query_reference_2):

  chat_history = ""
  prompt = "What color is the sky?"
  text_context = create_query_reference.document_text
  expected_prompt = QUESTION_PROMPT.format(
    question=prompt, chat_history=chat_history, context=text_context)
  question = "What color is the sky?"
  query_context = [create_query_reference]
  actual_prompt = get_question_prompt(
    question, chat_history, query_context
  )
  assert expected_prompt == actual_prompt, "Prompts don't match"

  prompt = "What color is the sky?"
  list_context = [create_query_reference.document_text,
                  create_query_reference_2.document_text]
  text_context = "\n\n".join(list_context)
  expected_prompt = QUESTION_PROMPT.format(
    question=prompt, chat_history=chat_history, context=text_context
  )
  question = "What color is the sky?"
  query_context = [create_query_reference,
                   create_query_reference_2]
  actual_prompt = get_question_prompt(
    question, chat_history, query_context
  )
  assert expected_prompt == actual_prompt, "Prompts don't match"
