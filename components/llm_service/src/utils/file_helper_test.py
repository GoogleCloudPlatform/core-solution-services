# Copyright 2024 Google LLC
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

"""
  Unit tests for LLM Service file helper utils
"""
# disabling pylint rules that conflict with pytest fixtures
# pylint: disable=unused-argument,redefined-outer-name,ungrouped-imports,unused-import,line-too-long
import numpy.testing as npt
import numpy as np
import pytest
from unittest import mock
from common.utils.logging_handler import Logger
from common.utils.config import set_env_var
from services.query.data_source import DataSourceFile
from utils.file_helper import process_chat_file

with set_env_var("PG_HOST", ""):
  from config import get_model_config

Logger = Logger.get_logger(__file__)

FAKE_DATA_SOURCE_FILES = [
  DataSourceFile(
      doc_name="fake web page",
      src_url="https://www.microsoft.com/en-us/investor/earnings/fy-2024-q3/press-release-webcast",
      local_path="/tmp/press-release-webcast.html",
      gcs_path="gs://fake-bucket/press-release-webcast.html",
      doc_id="xxx123",
      mime_type="text/html"
  ),
  DataSourceFile(
      doc_name="fake web page 2",
      src_url="http://www.x.com/press-release.html",
      local_path="/tmp/press-release.html",
      gcs_path="gs://fake-bucket/press-release.html",
      doc_id="xxx124",
      mime_type="text/html"
  ),
  DataSourceFile(
      doc_name="fake web page 3",
      src_url="http://x.com/a.pdf",
      local_path="/tmp/pdf",
      gcs_path="gs://pdf",
      doc_id="xxx125",
      mime_type="application/pdf"
  ),
]

class FakeUploadFile():
  def seek(self,b:int) -> int:
    return 0
  @property
  def size(self):
    return 1000

class FakeWebDataSource():
  def __init__(self, idx):
    self.idx = idx
  def download_documents(self, url, tempdir):
    return [FAKE_DATA_SOURCE_FILES[self.idx]]

class FakeStorageClient():
  def bucket(self):
    pass
  def list_blobs(self):
    pass

@pytest.mark.asyncio
@mock.patch("utils.file_helper.WebDataSource")
@mock.patch("google.cloud.storage.Client")
async def test_process_chat_file_web(mock_storage_client,
                                     mock_web_datasource):
  mock_web_datasource.return_value = FakeWebDataSource(0)
  fake_url = FAKE_DATA_SOURCE_FILES[0].src_url
  chat_files = await process_chat_file(None, fake_url)
  assert chat_files[0] == FAKE_DATA_SOURCE_FILES[0]

@pytest.mark.asyncio
@mock.patch("google.cloud.storage.Client")
async def test_process_chat_file_gcs(mock_storage_client):
  mock_storage_client.return_value = FakeStorageClient
  assert True


@pytest.mark.asyncio
@mock.patch("utils.file_helper.UploadFile")
async def test_process_chat_file_upload(mock_file_upload):
  mock_file_upload.return_value = FakeUploadFile
  assert True

