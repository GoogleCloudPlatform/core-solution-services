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
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response
from w3lib.html import replace_escape_chars
from bs4 import BeautifulSoup
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

  # Remove script and style and other irrelevant tags
  tags_to_remove = ["script", "style", "footer", "nav", "aside", "form", "meta",
                    "iframe", "header", "button", "input", "select", "textarea", 
                    "noscript", "img", "figure", "figcaption", "link"]
  for element in soup(tags_to_remove):
    element.decompose()

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


class WebDataSource(DataSource):
  """
   Web site data source.
  """

  def __init__(self, storage_client=None, bucket_name=None, depth_limit=1):
    """
    Initialize the WebDataSource.

    Args:
      start_urls: List of URLs to download.
      bucket_name (str): name of GCS bucket to save downloaded webpages.
                         If None files will not be saved.
      depth_limit (int): depth limit to crawl
    """
    if storage_client is None:
      storage_client = storage.Client()
    super().__init__(storage_client)
    self.depth_limit = depth_limit
    self.bucket_name = bucket_name
    self.doc_data = []

  def _item_scraped(self, item, response, spider):
    """Handler for the response_downloaded signal."""
    Logger.info(f"Downloaded Response URL: {response.url}")
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
    #
    if self.bucket_name:
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

    # Connect the item_scraped signal to the handler
    crawler.signals.connect(self._item_scraped,
                            signal=signals.item_scraped)
    process.crawl(crawler,
                  start_urls=[doc_url],
                  storage_client=self.storage_client,
                  bucket_name=self.bucket_name,
                  filepath=temp_dir)
    process.start()

    return self.doc_data

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
