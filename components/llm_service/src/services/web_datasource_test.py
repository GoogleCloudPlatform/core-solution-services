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

import unittest
import os
from scrapy.http import TextResponse, Request
from langchain.schema import Document
from services.web_datasource import WebDataSource, WebDataSourceSpider

class TestWebDataSource(unittest.TestCase):

  def setUp(self):
    # List of test URLs
    self.urls = ["https://example.com"]
    
    # Test filepath to save downloaded webpages
    self.filepath = "/tmp/test_downloads"
    os.makedirs(self.filepath)

    # Mock content
    self.mock_url_content = ("<html><body>Test Content</body></html>")

  def test_load(self):
    # Create an instance of WebDataSource with test URLs and filepath
    data_source = WebDataSource(self.urls, self.filepath)
    
    # Mock the response using Scrapy's TextResponse
    url = self.urls[0]
    request = Request(url)  # Create a Request object directly
    response = TextResponse(url=url, request=request,
                            body=self.mock_url_content, encoding='utf-8')
    
    # Simulate the parse method with the mocked response
    spider = WebDataSourceSpider(start_urls=self.urls, filepath=self.filepath)
    results = list(spider.parse(response))
    
    # Check if the documents are parsed correctly
    self.assertEqual(len(results), 1)
    self.assertEqual(results[0]["url"], url)
    self.assertEqual(results[0]["content"], self.mock_url_content)
    
    # Check if the webpages are saved to the specified filepath
    filename = os.path.join(self.filepath, url.split("/")[-1] + ".html")
    self.assertTrue(os.path.exists(filename))
    with open(filename, "r") as f:
      content = f.read()
      self.assertEqual(content, self.mock_url_content)

  def tearDown(self):
    # Cleanup: Remove the test_downloads directory and its contents
    for filename in os.listdir(self.filepath):
      os.remove(os.path.join(self.filepath, filename))
    os.rmdir(self.filepath)

if __name__ == "__main__":
  unittest.main()
