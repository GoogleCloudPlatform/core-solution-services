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

from config import TRUSS_LLM_LLAMA2_CHAT
from services.query.query_prompt_config import \
  QUESTION_PROMPT, SUMMARY_PROMPT, LLAMA2_QUESTION_PROMPT
from common.utils.logging_handler import Logger
from common.models import QueryReference

Logger = Logger.get_logger(__file__)

def get_question_prompt(prompt: str,
                        chat_history: str,
                        query_context: List[QueryReference],
                        llm_type: str) -> str:
  """ Create question prompt with context for LLM """
  Logger.info(f"Creating question prompt with context "
              f"for LLM prompt=[{prompt}]")
  #SC240930: MUST FIX FOR MULTIMODAL
  #SC240930: query_context is the list of QueryReferences, each of which
  #SC240930: can be text (in field document_text) or image (in chunk_url)
  #SC240930: So can't just append the text

  #SC240930: Even if the QueryReference is an image, it should still have
  #SC240930: a document_text field, right?  it would just be "", which is fine here, right?

  #SC240930: But if QueryReference is an image, still need to somehow build up
  #SC240930: a list of the chunk_urls, and pass it on
  #SC240930: No, don't bother with this.  Leave this as-is, working on text only.  Will build up list of image_urls elsewhere, to pass into llm_chat.
  #context_list = [ref.document_text for ref in query_context] #SC241001
  #context_list = [ref.document_text for ref in query_context if hasattr(ref, "document_text")] #SC241001
  #SC241001: if the QueryReference object is from an image chunk then it will not have a "document_text" field
  context_list = []
  for ref in query_context:
    if hasattr(ref, "modality") and ref.modality=="text":
      if hasattr(ref, "document_text"):
        context_list.append(ref.document_text)
  text_context = "\n\n".join(context_list)

  if llm_type == TRUSS_LLM_LLAMA2_CHAT:
    #SC240930: Must fix for multimodal
    #Sc240930: Don't bother.  Multimodal moat around Gemini.
    question = LLAMA2_QUESTION_PROMPT.format(
      question=prompt, chat_history=chat_history, context=text_context
    )
  else:
    #SC240930: MUST FIX FOR MULTIMODAL
    #SC240930: INPUT: prompt is always a string
    #SC240930: INPUT: chat_history is always a string
    #SC240930: INPUT: text_context is always a string
    #SC240930: NEW INPUT: Need to provide a list of chunk_urls, for those QueryReferences that are images
    #SC240930: OUTPUT: What is question? Is it just a string?

    #SC240930: OR leave this as-is, such that question only contains the text part of the prompt
    #SC240930: We can feed in the list of chunk_urls from the image-based QueryReferences later, directly into llm_chat?
    #SC240930: Yes do that
    question = QUESTION_PROMPT.format(
      question=prompt, chat_history=chat_history, context=text_context
    )
  #SC240930: CONCLUSION: get_question_prompt will return question, which is always a string
  #SC240930: question will contain the text from query_references, but not the image info from query_references
  #SC240930: So the text info from query_references will be passed into llm_chat via question
  #SC240930: But the image info from query_references will need to be passed in differently and separately to llm_chat
  Logger.info(f"#SC240930: About to exit get_question_prompt")
  return question

def get_summarize_prompt(original_text: str) -> str:
  """ Create summarize prompt for LLM """
  Logger.info(f"Creating summarize prompt for original text=[{original_text}]")
  prompt = SUMMARY_PROMPT.format(original_text=original_text)
  return prompt
