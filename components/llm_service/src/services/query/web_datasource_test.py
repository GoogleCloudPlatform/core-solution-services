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

""" Unit tests for web data sources for Query Engines """

import unittest
import os
from scrapy.http import TextResponse, Request
from services.query.web_datasource import WebDataSource, WebDataSourceSpider

class TestWebDataSource(unittest.TestCase):
  """ Unit tests for web data sources for Query Engines """
  def setUp(self):
    # List of test URLs
    self.urls = ["https://example.com"]

    # Test filepath to save downloaded webpages
    self.filepath = "/tmp/test_downloads"
    os.makedirs(self.filepath)

    # Mock headers
    self.mock_headers = {
      "Content-Type": "text/html; charset=utf-8",
      "Custom-Header": "Custom Value"
    }

    # Mock content
    self.mock_body_content = """
<html>
<head>
    <style>
        body { background-color: lightblue; }
        p { color: navy; }
    </style>
    <link rel="stylesheet" type="text/css" href="http://example.com/mystyle.css">
    <script>
        function myFunction() {
            alert("This is a mock script!");
        }
    </script>
</head>
<body>
    <p>Mocked Response</p>
    <button onclick="myFunction()">Click me</button>
</body>
</html>
"""

    self.cleaned_content = """
<html><head></head><body><p>Mocked Response</p></body></html>
""".strip("\n")

  def test_load(self):
    # Create an instance of WebDataSource with test URLs and filepath
    _ = WebDataSource(self.urls, self.filepath)

    # Mock the response using Scrapy's TextResponse
    url = self.urls[0]
    request = Request(url)  # Create a Request object directly
    response = TextResponse(url=url, request=request,
                            body=self.mock_body_content, encoding="utf-8",
                            headers=self.mock_headers)

    # Simulate the parse method with the mocked response
    spider = WebDataSourceSpider(start_urls=self.urls, filepath=self.filepath)
    results = spider.parse(response)

    # Check if the documents are parsed correctly
    self.assertEqual(results["url"], url)
    self.assertEqual(results["content"], self.cleaned_content)

    # Check if the webpages are saved to the specified filepath
    filename = os.path.join(self.filepath,
                            url.rsplit("/", maxsplit=1)[-1] + ".html")
    self.assertTrue(os.path.exists(filename))
    with open(filename, "r", encoding="utf-8") as f:
      content = f.read()
      self.assertEqual(content, self.cleaned_content)

  def tearDown(self):
    # Cleanup: Remove the test_downloads directory and its contents
    for filename in os.listdir(self.filepath):
      os.remove(os.path.join(self.filepath, filename))
    os.rmdir(self.filepath)


if __name__ == "__main__":
  unittest.main()
