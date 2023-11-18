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
from typing import List
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response
from w3lib.html import replace_escape_chars
from bs4 import BeautifulSoup
import os
import re
import hashlib
from google.cloud import storage
from common.utils.logging_handler import Logger
from services.query.data_source import DataSource

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

def clean_html(html_content:str) -> str:
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
  soup = BeautifulSoup(html_content, "html.parser")
  # Remove script and style tags
  for script_style_tag in soup(["script", "style"]):
    script_style_tag.decompose()
  # Remove <link> tags that are stylesheets
  for link_tag in soup.find_all("link", {"rel": "stylesheet"}):
    link_tag.decompose()
  # Get the cleaned HTML content
  cleaned_content = str(soup)
  # Replace HTML escape characters with their equivalents
  cleaned_content = replace_escape_chars(cleaned_content)
  return cleaned_content

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
  # Ensure the file name ends with ".html" or ".pdf"
  if not safe_filename.endswith((".html", ".pdf")):
    safe_filename += ".html"
  return safe_filename


class WebDataSourceSpider(CrawlSpider):
  """Scrapy spider to crawl and download webpages."""

  name = "web_data_source_spider"

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
    self.start_urls = start_urls
    if len(start_urls) == 0:
      msg = "URL list is empty"
      Logger.error(msg)
      raise Exception(msg)

    if restrict_domain:
      start_url = start_urls[0]
      domain = re.findall(r"://(.*?)/", start_url + "/")[0]
      self.allowed_domains = [domain]

    self.storage_client = storage_client
    self.bucket_name = bucket_name
    self.filepath = filepath
    self.crawled_urls = []
    self.rules = (
      Rule(LinkExtractor(allow_domains=self.allowed_domains),
           callback="parse", follow=True),
    )
    super()._compile_rules()

  def closed(self, reason: str):
    print(reason)
    for url in self.crawled_urls:
      print(url)
    pass

  def parse(self, response: Response, **kwargs) -> dict:
    content_type = response.headers.get("Content-Type").decode("utf-8")
    self.crawled_urls.append(response.url)

    # Check if the content type is HTML
    if "text/html" in content_type:
      file_content = clean_html(response.text)
    elif "application/pdf" in content_type:
      file_content = response.body
    else:
      # Skip saving the content
      return {
        "url": response.url,
        "content_type": content_type,
        "content": response.body
      }

    file_name = sanitize_url(response.url)
    item_metadata = {
      "url": response.url,
      "filename": file_name,
      "bucket_name": self.bucket_name,
      "filepath": self.filepath,
      "content_type": content_type,
      "content": file_content
    }
    if self.storage_client and self.bucket_name:
      upload_to_gcs(self.storage_client, self.bucket_name,
                    file_name, file_content, content_type)
    else:
      save_content(self.filepath, file_name, file_content)
    return item_metadata

class WebDataSource(DataSource):
  """Document loader that uses Scrapy to download webpages."""

  def __init__(self, start_urls, depth_limit=1,
               storage_client=None, bucket_name=None, filepath="/tmp"):
    """
    Initialize the WebDataSource.

    Args:
      start_urls: List of URLs to download.
      bucket_name: GCS bucket to save downloaded webpages.
    """
    if storage_client is None:
      storage_client = storage.Client()
    super().__init__(storage_client)
    self.storage_client = storage_client
    self.start_urls = start_urls
    self.depth_limit = depth_limit
    self.bucket_name = bucket_name
    self.filepath = filepath
    self.crawled_urls = []

  def _response_downloaded(self, response):
    """Handler for the response_downloaded signal."""
    Logger.info(f"Downloaded Response URL: {response.url}")
    self.crawled_urls.append(response.url)

  def load(self) -> List[str]:
    """
    Load the webpages and return them as a list of Document objects.

    Returns:
      List of Document objects.
    """
    clear_bucket(self.storage_client, self.bucket_name)
    # Define the Scrapy settings
    settings = {
      "ROBOTSTXT_OBEY": False,
      "DEPTH_LIMIT": self.depth_limit,
      # Add other Scrapy settings as needed
    }
    # Start the Scrapy process
    process = CrawlerProcess(settings=settings)
    crawler = process.create_crawler(WebDataSourceSpider)

    # Connect the response_downloaded signal to the handler
    crawler.signals.connect(self._response_downloaded,
                            signal=signals.response_downloaded)
    process.crawl(crawler,
                  start_urls=self.start_urls,
                  storage_client=self.storage_client,
                  bucket_name=self.bucket_name,
                  filepath=self.filepath)
    process.start()

    return self.crawled_urls


if __name__ == "__main__":
  base_url = ["https://dmv.nv.gov//"]
  gcs_bucket = "gcp-mira-demo-test"
  start_time = datetime.now()
  # WebDataSource(start_url="https://www.medicaid.gov/sitemap/index.html",
  #               depth_limit=1, bucket_name="gcp-mira-demo-medicaid-test")
  web_datasource = WebDataSource(start_urls=base_url,
                                 depth_limit=1,
                                 bucket_name=gcs_bucket)
  crawled_urls = web_datasource.load()
  time_elapsed = datetime.now() - start_time
  Logger.info(f"Time elapsed (hh:mm:ss.ms) {time_elapsed}")
  Logger.info(f"Scraped {len(crawled_urls)} links")
  for crawled_url in crawled_urls:
    print(crawled_url)
