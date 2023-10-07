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
import os

class WebDataSourceSpider(scrapy.Spider):
  """Scrapy spider to crawl and download webpages."""
  
  name = "web_data_source_spider"
  
  def __init__(self, start_urls=None, filepath=None, *args, **kwargs):
    """
    Initialize the spider.
    
    Args:
      start_urls: List of URLs to start crawling from.
      filepath: Directory path to save downloaded webpages.
    """
    super(WebDataSourceSpider, self).__init__(*args, **kwargs)
    self.start_urls = start_urls or []
    self.filepath = filepath

  def parse(self, response):
    """
    Parse the downloaded webpage and save its content.
    
    Args:
      response: The response object containing webpage data.
    """
    # Save the content to the specified filepath
    if self.filepath:
      with open(os.path.join(self.filepath, 
                             response.url.split("/")[-1] + ".html"), "w") as f:
        f.write(response.text)
    
    # Extract data and save or process it
    yield {
      "url": response.url,
      "content": response.text
    }

class WebDataSource(BaseLoader):
  """Document loader that uses Scrapy to download webpages."""

  def __init__(self, urls, filepath=None):
    """
    Initialize the WebDataSource.
    
    Args:
      urls: List of URLs to download.
      filepath: Directory path to save downloaded webpages.
    """
    self.urls = urls
    self.filepath = filepath
    self.documents = []

  def load(self) -> List[Document]:
    """
    Load the webpages and return them as a list of Document objects.
    
    Returns:
      List of Document objects.
    """
    # Define the Scrapy settings
    settings = {
      "USER_AGENT": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/58.0.3029.110 Safari/537.3"),
      "ROBOTSTXT_OBEY": True
    }

    # Start the Scrapy process
    process = CrawlerProcess(settings=settings)
    process.crawl(WebDataSourceSpider, start_urls=self.urls, filepath=self.filepath)
    process.start()

    # Convert crawled data to Document objects
    for data in self.documents:
      yield Document(url=data["url"], content=data["content"])

  def lazy_load(self) -> Iterator[Document]:
    """
    Lazily load the webpages and yield them as Document objects.
    
    Returns:
      Iterator of Document objects.
    """
    for doc in self.load():
      yield doc
