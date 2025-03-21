# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable = broad-except

"""class and methods for logs handling."""

import logging
import os
import sys
from common.config import CLOUD_LOGGING_ENABLED
import google.cloud.logging

# Create a filter to add missing fields
class LogRecordFilter(logging.Filter):
  """Filter to ensure required fields are present in log records."""

  def filter(self, record):
    # Add default values for required fields if they don't exist
    if not hasattr(record, 'request_id'):
      record.request_id = '-'
    if not hasattr(record, 'trace'):
      record.trace = '-'
    return True

# Helper function to add default fields
def _add_default_fields(extra=None):
  """Add default fields to extra dictionary."""
  if extra is None:
    extra = {}
  if 'request_id' not in extra:
    extra['request_id'] = '-'
  if 'trace' not in extra:
    extra['trace'] = '-'
  return extra

# Set up cloud logging client
if CLOUD_LOGGING_ENABLED:
  try:
    client = google.cloud.logging.Client()
  except Exception:
    print('Failed to initialize Cloud Logging client, falling back to stdout')
    client = None
else:
  client = None

# Configure root logger once
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)

# Add our filter to the root logger
root_filter = LogRecordFilter()
if root_filter not in root_logger.filters:
  root_logger.addFilter(root_filter)

# Common log format
log_format = (
  '%(asctime)s:%(levelname)s: [%(name)s:%(lineno)d - %(funcName)s()] '
  'request_id=%(request_id)s trace=%(trace)s %(message)s'
)
formatter = logging.Formatter(log_format)

# Set up handlers only once
if not root_logger.handlers:
  if CLOUD_LOGGING_ENABLED and client:
    cloud_handler = client.get_default_handler()
    cloud_handler.setFormatter(formatter)
    root_logger.addHandler(cloud_handler)
  else:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

# Create a global class logger
_static_logger = logging.getLogger('Logger')
_static_logger.setLevel(logging.INFO)
_static_logger.addFilter(LogRecordFilter())

# Define the instance logger class
class Logger:
  """Instance logger for module-specific logging."""

  def __init__(self, name):
    try:
      dirname = os.path.dirname(name)
      filename = os.path.split(name)[1]
      folder = os.path.split(dirname)[1] if dirname else 'root'
      module_name = f'{folder}/{filename}'
    except (IndexError, AttributeError):
      module_name = str(name)

    self.logger = logging.getLogger(module_name)
    self.logger.setLevel(logging.INFO)
    self.logger.addFilter(LogRecordFilter())

  @classmethod
  def get_logger(cls, name) -> logging.Logger:
    logger_instance = cls(name)
    return logger_instance.logger

  # Instance logging methods
  def info(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    kwargs['extra'] = _add_default_fields(extra)
    self.logger.info(msg, *args, **kwargs)

  def error(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    kwargs['extra'] = _add_default_fields(extra)
    self.logger.error(msg, *args, **kwargs)

  def warning(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    kwargs['extra'] = _add_default_fields(extra)
    self.logger.warning(msg, *args, **kwargs)

  def debug(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    kwargs['extra'] = _add_default_fields(extra)
    self.logger.debug(msg, *args, **kwargs)

  def critical(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    kwargs['extra'] = _add_default_fields(extra)
    self.logger.critical(msg, *args, **kwargs)

  def exception(self, msg, *args, **kwargs):
    extra = kwargs.get('extra', {})
    kwargs['extra'] = _add_default_fields(extra)
    self.logger.exception(msg, *args, **kwargs)

# Define static methods at module level
def info(msg, *args, **kwargs):
  """Static info logger."""
  extra = kwargs.get('extra', {})
  kwargs['extra'] = _add_default_fields(extra)
  _static_logger.info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
  """Static error logger."""
  extra = kwargs.get('extra', {})
  kwargs['extra'] = _add_default_fields(extra)
  _static_logger.error(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
  """Static warning logger."""
  extra = kwargs.get('extra', {})
  kwargs['extra'] = _add_default_fields(extra)
  _static_logger.warning(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
  """Static debug logger."""
  extra = kwargs.get('extra', {})
  kwargs['extra'] = _add_default_fields(extra)
  _static_logger.debug(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
  """Static critical logger."""
  extra = kwargs.get('extra', {})
  kwargs['extra'] = _add_default_fields(extra)
  _static_logger.critical(msg, *args, **kwargs)

def exception(msg, *args, **kwargs):
  """Static exception logger."""
  extra = kwargs.get('extra', {})
  kwargs['extra'] = _add_default_fields(extra)
  _static_logger.exception(msg, *args, **kwargs)

Logger.info = staticmethod(info)
Logger.error = staticmethod(error)
Logger.warning = staticmethod(warning)
Logger.debug = staticmethod(debug)
Logger.critical = staticmethod(critical)
Logger.exception = staticmethod(exception)
