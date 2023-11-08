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
from services.query_prompts import question_prompt
from services.query_prompt_config import QUESTION_PROMPT


def test_question_prompt():

  prompt = "What color is the sky?"
  text_context = "It is sunny outside, the sky is blue."
  expected_prompt = QUESTION_PROMPT.format(
    question=prompt, context=text_context)
  question = "What color is the sky?"
  query_context = [{"document_text": "It is sunny outside, the sky is blue."}]
  actual_prompt = question_prompt(question, query_context)
  assert expected_prompt == actual_prompt, "Prompts don't match"

  prompt = "What color is the sky?"
  list_context = ["It is sunny outside, the sky is blue.",
                  "And there are no clouds."]
  text_context = "\n\n".join(list_context)
  expected_prompt = QUESTION_PROMPT.format(
    question=prompt, context=text_context)
  question = "What color is the sky?"
  query_context = [{"document_text": "It is sunny outside, the sky is blue."},
                   {"document_text": "And there are no clouds."}]
  actual_prompt = question_prompt(question, query_context)
  assert expected_prompt == actual_prompt, "Prompts don't match"
