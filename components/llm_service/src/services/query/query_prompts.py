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
Query prompt generator methods
"""
from typing import List

from services.query.query_prompt_config import QUESTION_PROMPT, SUMMARY_PROMPT
from common.utils.logging_handler import Logger
from common.models import QueryReference

Logger = Logger.get_logger(__file__)

def get_question_prompt(prompt: str,
                        chat_history: str,
                        query_context: List[QueryReference]) -> str:
  """ Create question prompt with context for LLM """
  Logger.info(f"Creating question prompt with context "
              f"for LLM prompt=[{prompt}]")
  context_list = [ref.document_text for ref in query_context]
  text_context = "\n\n".join(context_list)
  question = QUESTION_PROMPT.format(
    question=prompt, chat_history=chat_history, context=text_context
  )
  return question

def get_summarize_prompt(original_text: str) -> str:
  """ Create summarize prompt for LLM """
  Logger.info(f"Creating summarize prompt for original text=[{original_text}]")
  prompt = SUMMARY_PROMPT.format(original_text=original_text)
  return prompt
