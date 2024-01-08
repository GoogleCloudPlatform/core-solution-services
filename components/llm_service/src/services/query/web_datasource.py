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
Web data sources for Query Engines
"""
from datetime import datetime
import re
import hashlib
import os
import sys
import tempfile
from typing import List, Tuple
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule, Spider
from scrapy.http import Response
from google.cloud import storage
from config import DEFAULT_WEB_DEPTH_LIMIT
from common.utils.logging_handler import Logger
from services.query.data_source import DataSource
from utils.html_helper import (html_trim_tags,
                               html_to_text,
                               html_to_sentence_list)

Logger = Logger.get_logger(__file__)


def clear_bucket(storage_client:storage.Client, bucket_name:str) -> None:
  """
  Delete all the contents of the specified GCS bucket
  """
  Logger.info(f"Deleting all objects from GCS bucket {bucket_name}")
  bucket = storage_client.bucket(bucket_name)
  blobs = bucket.list_blobs()
  index = 0
  for blob in blobs:
    blob.delete()
    index += 1
  Logger.info(f"{index} files deleted")

def upload_to_gcs(storage_client:storage.Client, bucket_name:str,
                  file_name:str, content:str,
                  content_type="text/plain") -> None:
  """Upload content to GCS bucket"""
  Logger.info(f"Uploading {file_name} to GCS bucket {bucket_name}")
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(file_name)
  blob.upload_from_string(
    data=content,
    content_type=content_type
  )
  Logger.info(f"Uploaded {len(content)} bytes")

def save_content(filepath:str, file_name:str, content:str) -> None:
  """
  Save content in a file in a local directory
  """
  Logger.info(f"Saving {file_name} to {filepath}")
  doc_filepath = os.path.join(filepath, file_name)
  with open(doc_filepath, "w", encoding="utf-8") as f:
    f.write(content)
  Logger.info(f"{len(content)} bytes written")

def sanitize_url(url) -> str:
  # Remove the scheme (http, https) and domain, and keep the path and query
  url_path = url.split("//", 1)[-1].split("/", 1)[-1]

  # Replace invalid file name characters with underscores
  safe_filename = re.sub(r"[^a-zA-Z0-9_\-.]", "_", url_path)

  # Truncate if the file name is too long
  max_length = 200  # Maximum length for file names
  if len(safe_filename) > max_length:
    # Create a hash of the full path to append to the truncated path
    # and use first 10 characters of hash
    hash_suffix = hashlib.md5(url.encode()).hexdigest()[:10]
    safe_filename = safe_filename[:max_length-11] + "_" + hash_suffix

  # Ensure the file name ends with ".html" or ".htm" or ".pdf"
  if not safe_filename.endswith((".html", ".pdf", ".htm")):
    safe_filename += ".html"

  return safe_filename

class WebDataSourceParser:
  """ This class is used a parser for all our scrapy spider classes """

  def __init__(self, storage_client=None, bucket_name=None, filepath="/tmp"):
    self.storage_client = storage_client
    self.bucket_name = bucket_name
    self.filepath = filepath
    self.crawled_urls = []

  def parse(self, response: Response, **kwargs) -> dict:
    content_type = response.headers.get("Content-Type").decode("utf-8")
    self.crawled_urls.append(response.url)

    # Check if the content type is HTML
    if "text/html" in content_type:
      file_content = html_trim_tags(response.text)
    elif "application/pdf" in content_type:
      file_content = response.body
    else:
      # Skip saving the content
      return {
        "url": response.url,
        "content_type": content_type,
        "content": None
      }

    file_name = sanitize_url(response.url)
    item = {
      "url": response.url,
      "filename": file_name,
      "bucket_name": self.bucket_name,
      "filepath": self.filepath,
      "content_type": content_type,
      "content": file_content
    }
    save_content(self.filepath, file_name, file_content)
    if self.storage_client and self.bucket_name:
      upload_to_gcs(self.storage_client, self.bucket_name,
                    file_name, file_content, content_type)
    return item


class WebDataSourcePageSpider(Spider):
  """Scrapy spider to download individual webpages."""
  name = "web_data_source_page_spider"

  def __init__(self, *args, start_urls=None,
               storage_client=None, bucket_name=None, filepath="/tmp",
               **kwargs):
    super().__init__(*args, **kwargs)
    self.start_urls = start_urls
    self.parser = WebDataSourceParser(
        storage_client=storage_client,
        bucket_name=bucket_name,
        filepath=filepath)

  def parse(self, response: Response, **kwargs) -> dict:
    return self.parser.parse(response, **kwargs)


class WebDataSourceSpider(CrawlSpider):
  """Scrapy spider to crawl and download webpages."""

  name = "web_data_source_crawl_spider"

  def __init__(self, *args, start_urls=None, restrict_domain=True,
               storage_client=None, bucket_name=None, filepath="/tmp",
               **kwargs):
    """
    Initialize the spider.
    Args:
      start_urls: List of URLs to download
      restrict_domain: Restrict domain to the original URL
      storage_client: Python Storage client for GCS
      bucket_name: GCS bucket save downloaded webpages
      filepath: Used mainly for testing (if bucket_name is empty)
    """
    super().__init__(*args, **kwargs)
    self.parser = WebDataSourceParser(
        storage_client=storage_client,
        bucket_name=bucket_name,
        filepath=filepath)

    self.start_urls = start_urls
    if len(start_urls) == 0:
      msg = "URL list is empty"
      Logger.error(msg)
      raise Exception(msg)

    if restrict_domain:
      start_url = start_urls[0]
      domain = re.findall(r"://(.*?)/", start_url + "/")[0]
      self.allowed_domains = [domain]

    self.rules = (
      Rule(LinkExtractor(allow_domains=self.allowed_domains),
           callback="parse", follow=True),
    )
    super()._compile_rules()

  def closed(self, reason: str):
    print(reason)
    for url in self.parser.crawled_urls:
      print(url)
    pass

  def parse(self, response: Response, **kwargs) -> dict:
    return self.parser.parse(response, **kwargs)



class WebDataSource(DataSource):
  """
   Web site data source.
  """

  def __init__(self,
               storage_client=None,
               bucket_name=None,
               depth_limit=DEFAULT_WEB_DEPTH_LIMIT):
    """
    Initialize the WebDataSource.

    Args:
      start_urls: List of URLs to download.
      bucket_name (str): name of GCS bucket to save downloaded webpages.
                         If None files will not be saved.
      depth_limit (int): depth limit to crawl. 0=don't crawl, just
                         download provided URLs
    """
    if storage_client is None:
      storage_client = storage.Client()
    super().__init__(storage_client)
    self.depth_limit = depth_limit
    self.bucket_name = bucket_name
    self.doc_data = []

  def _item_scraped(self, item, response, spider):
    """Handler for the item_scraped signal."""
    Logger.info(f"Downloaded Response URL: {response.url}")
    content_type = item["content_type"]
    if item["content"] is None:
      Logger.warn(
        f"No content from: {response.url}, content type: {content_type}")
    else:
      filepath = os.path.join(item["filepath"], item["filename"])
      self.doc_data.append((item["filename"],
                            item["url"],
                            filepath))

  def download_documents(self, doc_url: str, temp_dir: str) -> \
        List[Tuple[str, str, str]]:
    """
    Download files from doc_url source to a local tmp directory

    Args:
        doc_url: url pointing to container of documents to be indexed
        temp_dir: Path to temporary directory to download files to

    Returns:
        list of tuples (doc name, document url, local file path)
    """
    # clear bucket
    if self.bucket_name:
      clear_bucket(self.storage_client, self.bucket_name)

    if self.depth_limit == 0:
      # for this class, depth_limit=0 means don't crawl, just download the
      # web page(s) supplied.  (for scrapy depth_limit=0 means no limit).
      spider_class = WebDataSourcePageSpider
    elif self.depth_limit > 0:
      spider_class = WebDataSourceSpider

    # define Scrapy settings
    settings = {
      "ROBOTSTXT_OBEY": False,
      "DEPTH_LIMIT": self.depth_limit,
      "LOG_LEVEL": "INFO"
    }
    # create the Scrapy crawler process
    process = CrawlerProcess(settings=settings)
    crawler = process.create_crawler(spider_class)

    # Connect the item_scraped signal to the handler
    crawler.signals.connect(self._item_scraped,
                            signal=signals.item_scraped)

    # start the scrapy crawler
    process.crawl(crawler,
                  start_urls=[doc_url],
                  storage_client=self.storage_client,
                  bucket_name=self.bucket_name,
                  filepath=temp_dir)
    process.start()

    return self.doc_data

  @classmethod
  def text_to_sentence_list(cls, text: str) -> List[str]:
    return html_to_sentence_list(text)

  @classmethod
  def clean_text(cls, text: str) -> List[str]:
    html_text = html_to_text(text)
    return cls.clean_text(html_text)


def main():
  args = ["genie-demo-gdch-web", "https://dmv.nv.gov//", 1]
  if len(sys.argv) > 1:
    args = sys.argv[1:]
  bucket,url,depth = args
  start_time = datetime.now()
  # WebDataSource(start_url="https://www.medicaid.gov/sitemap/index.html",
  #               depth_limit=1, bucket_name="gcp-mira-demo-medicaid-test")
  web_datasource = WebDataSource(bucket_name=bucket,
                                 depth_limit=depth)
  temp_dir = tempfile.mkdtemp()
  doc_data = web_datasource.download_documents(url, temp_dir)
  time_elapsed = datetime.now() - start_time
  Logger.info(f"Time elapsed (hh:mm:ss.ms) {time_elapsed}")
  Logger.info(f"Scraped {len(doc_data)} links")
  crawled_urls = [d[1] for d in doc_data]
  print(crawled_urls)
  print(f"*** Pages stored at [{temp_dir}]")

if __name__ == "__main__":
  main()
