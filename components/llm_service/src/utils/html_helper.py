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

# pylint: disable=unused-argument,broad-exception-raised
"""
HTML helper functions.
"""

from w3lib.html import replace_escape_chars
from bs4 import BeautifulSoup, Comment


TAGS_TO_REMOVE = ["script", "style", "footer", "nav", "aside", "form", "meta",
                  "iframe", "header", "button", "input", "select", "textarea",
                  "noscript", "img", "figure", "figcaption", "link"]


def get_clean_html_soup(
    html_content:str, tags_to_trim:list = None) -> BeautifulSoup:
  """Get BeautifulSoup object with cleaned tags and context.
     It removes tags in TAGS_TO_REMOVE by default.

  Args:
      html_content (str): The HTML content.
      tags_to_trim (str): List of tags to remove.
  Returns:
      BeautifulSoup: Soup object for further operation.
  """
  soup = BeautifulSoup(html_content, "html.parser")
  if not tags_to_trim:
    tags_to_trim = TAGS_TO_REMOVE

  # Remove script and style and other irrelevant tags
  for element in soup(tags_to_trim):
    element.decompose()

  # remove HTML comments
  comments = soup.find_all(string=lambda text: isinstance(text, Comment))
  for comment in comments:
    comment.extract()

  # Remove all attributes except href from <a> tags
  # and all attributes from other tags
  for tag in soup.find_all(True):
    if tag.name == "a":
      href = tag.get("href")
      tag.attrs = {}
      if href:
        tag["href"] = href
    else:
      tag.attrs = {}

  return soup

def html_to_text(html_content:str, tags_to_trim:list = None) -> str:
  """Return text from a html content.

  Args:
      html_content (str): The HTML content.
  Returns:
      BeautifulSoup: Soup object for further operation.
  """
  soup = get_clean_html_soup(html_content, tags_to_trim)
  clean_text = replace_escape_chars(soup.get_text(separator=" "))
  return clean_text

def html_to_sentence_list(html_content:str, tags_to_trim:list = None) -> list:
  # TODO: Replace this with better splitter, e.g.
  # https://python.langchain.com/docs/modules/data_connection/document_transformers/text_splitters/split_by_token

  SENTENCE_TAGS = ["p", "ul"]
  soup = get_clean_html_soup(html_content, tags_to_trim)

  sentences = []
  for element in soup.find_all(SENTENCE_TAGS):
    if element.name == "ul":
      items = []
      for li in element.find_all("li"):
        items.append(li.get_text())
      sentences.append(" ".join(items))
    else:
      sentences.append(element.get_text())

  return sentences

def html_trim_tags(html_content:str, tags_to_trim:list = None) -> str:
  """
  Remove all <script> tags and their content from the given HTML content.
  Remove all <style> tags and <link> tags that reference stylesheets
  from the given HTML content.
  Args:
      html_content (str): The HTML content.
  Returns:
      str: The HTML content without <script> tags and CSS references.
  """
  # Parse the HTML content
  soup = get_clean_html_soup(html_content, tags_to_trim)

  # Replace HTML escape characters with their equivalents
  clean_text = replace_escape_chars(str(soup))
  return clean_text
