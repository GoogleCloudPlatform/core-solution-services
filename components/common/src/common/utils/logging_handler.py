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

"""class and methods for logs handling."""

import logging
import os
import sys
from common.config import CLOUD_LOGGING_ENABLED
import google.cloud.logging

if CLOUD_LOGGING_ENABLED:
  client = google.cloud.logging.Client()
else:
  client = None

class Logger:
  """class def handling logs."""

  def __init__(self, name):
    dirname = os.path.dirname(name)
    filename = os.path.split(name)[1]
    folder = os.path.split(dirname)[1]
    module_name = f'{folder}/{filename}'
    self.logger = logging.getLogger(module_name)
    self.logger.setLevel(logging.INFO)
    self.logger.propagate = False

    log_format = (
      '%(asctime)s:%(levelname)s: [%(name)s:%(lineno)d - %(funcName)s()] '
      'request_id=%(request_id)s trace=%(trace)s %(message)s'
    )
    formatter = logging.Formatter(log_format)

    if CLOUD_LOGGING_ENABLED and client:
      # Use the Cloud Logging handler
      cloud_handler = client.get_default_handler()
      cloud_handler.setFormatter(formatter)
      self.logger.addHandler(cloud_handler)
    else:
      handler = logging.StreamHandler(sys.stdout)
      handler.setFormatter(formatter)
      self.logger.addHandler(handler)

  @classmethod
  def get_logger(cls, name) -> logging.Logger:
    logger_instance = cls(name)
    return logger_instance.logger

  def _add_default_fields(self, record):
    if not hasattr(record, 'request_id'):
      record.request_id = '-'
    if not hasattr(record, 'trace'):
      record.trace = '-'

  def info(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    self._add_default_fields(extra)
    kwargs['extra'] = extra
    self.logger.info(msg, *args, **kwargs)

  def error(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    self._add_default_fields(extra)
    kwargs['extra'] = extra
    self.logger.error(msg, *args, **kwargs)

  def warning(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    self._add_default_fields(extra)
    kwargs['extra'] = extra
    self.logger.warning(msg, *args, **kwargs)

  def debug(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    self._add_default_fields(extra)
    kwargs['extra'] = extra
    self.logger.debug(msg, *args, **kwargs)

  def critical(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    self._add_default_fields(extra)
    kwargs['extra'] = extra
    self.logger.critical(msg, *args, **kwargs)

  def exception(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    self._add_default_fields(extra)
    kwargs['extra'] = extra
    self.logger.exception(msg, *args, **kwargs)
