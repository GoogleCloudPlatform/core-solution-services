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

import scrapy
from scrapy.crawler import CrawlerProcess
from typing import List, Iterator
from langchain.document_loaders.blob_loaders import Blob
from langchain.schema import Document
from langchain.document_loaders.base import BaseLoader

class WebDataSourceSpider(scrapy.Spider):
  name = "web_data_source_spider"
  
  def __init__(self, start_urls=None, *args, **kwargs):
    super(WebDataSourceSpider, self).__init__(*args, **kwargs)
    self.start_urls = start_urls or []

  def parse(self, response):
    # This method will be called for each URL in start_urls
    # Extract data and save or process it
    yield {
      "url": response.url,
      "content": response.text
    }

class WebDataSource(BaseLoader):

  def __init__(self, urls):
    self.urls = urls
    self.documents = []

  def load(self) -> List[Document]:
    # Define the Scrapy settings
    settings = {
      "USER_AGENT": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/58.0.3029.110 Safari/537.3"),
      "ROBOTSTXT_OBEY": True
    }

    # Start the Scrapy process
    process = CrawlerProcess(settings=settings)
    process.crawl(WebDataSourceSpider, start_urls=self.urls)
    process.start()

    # Convert crawled data to Document objects
    for data in self.documents:
      yield Document(url=data["url"], content=data["content"])

  def lazy_load(self) -> Iterator[Document]:
    # This method will be a generator that yields Document objects
    for doc in self.load():
      yield doc
