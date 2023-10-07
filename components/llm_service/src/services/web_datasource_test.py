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
from langchain.schema import Document
from services.web_datasource import WebDataSource

class TestWebDataSource(unittest.TestCase):

    def setUp(self):
        # List of test URLs (you can use mock URLs or real ones)
        self.urls = ["https://example.com"]
        
        # Test filepath to save downloaded webpages
        self.filepath = "test_downloads"

    def test_load(self):
        # Create an instance of WebDataSource with test URLs and filepath
        data_source = WebDataSource(self.urls, self.filepath)
        
        # Load the data
        documents = data_source.load()
        
        # Check if the documents are loaded correctly
        self.assertIsInstance(documents, list)
        self.assertTrue(all(isinstance(doc, Document) for doc in documents))
        
        # Check if the webpages are saved to the specified filepath
        for doc in documents:
            filename = os.path.join(self.filepath, doc.url.split("/")[-1] + ".html")
            self.assertTrue(os.path.exists(filename))

    def tearDown(self):
        # Cleanup: Remove the test_downloads directory and its contents
        for filename in os.listdir(self.filepath):
            os.remove(os.path.join(self.filepath, filename))
        os.rmdir(self.filepath)

if __name__ == "__main__":
    unittest.main()
