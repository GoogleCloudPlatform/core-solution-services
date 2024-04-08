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
OneDrive Config
"""
# pylint: disable=broad-exception-caught

from common.utils.logging_handler import Logger
from common.utils.secrets import get_secret
from common.utils.config import get_env_setting
from google.cloud import secretmanager

Logger = Logger.get_logger(__file__)


ONEDRIVE_CLIENT_ID = get_env_setting("ONEDRIVE_CLIENT_ID", None)
ONEDRIVE_TENANT_ID = get_env_setting("ONEDRIVE_TENANT_ID", None)

Logger.info(f"ONEDRIVE_CLIENT_ID = [{ONEDRIVE_CLIENT_ID}]")
Logger.info(f"ONEDRIVE_TENANT_ID = [{ONEDRIVE_TENANT_ID}]")

# load secrets

ONEDRIVE_CLIENT_SECRET = None
ONEDRIVE_PRINCIPLE_NAME = None

secrets = secretmanager.SecretManagerServiceClient()
try:
  ONEDRIVE_CLIENT_SECRET = get_secret("onedrive-client-secret")
except Exception as e:
  Logger.warning("Can't access onedrive client secret")
  ONEDRIVE_CLIENT_SECRET = None

try:
  ONEDRIVE_PRINCIPLE_NAME = get_secret("onedrive-principle-name")
except Exception as e:
  Logger.warning("Can't access onedrive principle name")
  ONEDRIVE_PRINCIPLE_NAME = None
