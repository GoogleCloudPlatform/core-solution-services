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
Text processing helper functions.
"""
# pylint: disable=broad-exception-caught

import re
from typing import List
from common.utils.logging_handler import Logger
import spacy

Logger = Logger.get_logger(__file__)


# global spacy object for nlp processes
nlp = None

try:
  # to use this model one must execute
  # python -m spacy download en_core_web_sm
  # in deployed llm_service this is done in the docker container build
  nlp = spacy.load("en_core_web_sm")
  Logger.info("loaded spacy model")
except Exception:
  # we fallback to sentencizer which doesn't require a download
  from spacy.lang.en import English

  nlp = English()
  nlp.add_pipe("sentencizer")
  Logger.info("using default spacy model")


def clean_text(text):
  # Replace specific unprocessable characters
  cleaned_text = text.replace("\x00", "")

  # remove all non-printable characters
  cleaned_text = re.sub(r"[^\x20-\x7E]", "", cleaned_text)

  return cleaned_text

def text_to_sentence_list(text: str) -> List[str]:
  # use spacy to split text into sentences
  cleaned_text = clean_text(text)
  document = nlp(cleaned_text)
  sentences = document.sents
  sentences = [str(x) for x in list(sentences)]
  return sentences

