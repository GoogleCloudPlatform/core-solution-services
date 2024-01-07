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

import re
from typing import List
import spacy
from w3lib.html import replace_escape_chars

"""
Text processing helper functions.
"""

# global spacy object for nlp processes
nlp = spacy.load("en_core_web_sm")

def clean_text(text):
  # Replace specific unprocessable characters
  cleaned_text = text.replace("\x00", "")

  # replace escape characters
  cleaned_text = replace_escape_chars(cleaned_text)

  # remove all non-printable characters
  cleaned_text = re.sub(r"[^\x20-\x7E]", "", cleaned_text)

  return cleaned_text

def text_to_sentence_list(text: str) -> List[str]:
  # use spacy to split text into sentences
  cleaned_text = clean_text(text)
  document = nlp(cleaned_text)
  sentences = document.sents
  sentences = [x for x in sentences if x.strip() != ""]
  return sentences

