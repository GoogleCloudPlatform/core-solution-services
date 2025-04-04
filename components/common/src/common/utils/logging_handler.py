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

# pylint: disable = broad-except

"""class and methods for logs handling."""

import json
import logging
import os
import sys
from common.config import CLOUD_LOGGING_ENABLED


# Create a filter to add missing fields
class LogRecordFilter(logging.Filter):
  """Filter to ensure required fields are present in log records."""

  def filter(self, record):
    # Add default values for required fields if they don"t exist
    if not hasattr(record, "app_request_id"):
      record.app_request_id = "-"
    if not hasattr(record, "gcp_trace_id"):
      record.gcp_trace_id = "-"
    if not hasattr(record, "trace"):
      record.trace = "-"
    return True

# Helper function to add default fields
def _add_default_fields(extra=None):
  """Add default fields to extra dictionary."""
  if extra is None:
    extra = {}
  if "app_request_id" not in extra:
    extra["app_request_id"] = "-"
  if "gcp_trace_id" not in extra:
    extra["gcp_trace_id"] = "-"
  if "trace" not in extra:
    extra["trace"] = "-"
  return extra

# Custom JSON formatter for structured logging
class JsonFormatter(logging.Formatter):
  """JSON formatter for structured logging that preserves extra fields."""

  def format(self, record):
    # Get basic log record info
    log_entry = {
      "message": record.getMessage(),
      "severity": record.levelname,
      "logger": record.name,
      "file": record.pathname,
      "line": record.lineno,
      "function": record.funcName,
      "app_request_id": getattr(record, "app_request_id", "-"),
      "gcp_trace_id": getattr(record, "gcp_trace_id", "-"),
      "trace": getattr(record, "trace", "-")
    }

    # Add any extra fields from the record
    for key, value in record.__dict__.items():
      if (key not in log_entry and 
          key not in ["args", "asctime", "created", "exc_info", "exc_text", 
                    "filename", "levelno", "module", "msecs", "msg", 
                    "name", "pathname", "process", "processName", 
                    "relativeCreated", "stack_info", "thread", "threadName"]):
        log_entry[key] = value

    return json.dumps(log_entry)

# Force reconfiguration of root logger by removing existing handlers
root_logger = logging.getLogger()
print(f"*** STARTUP: Root logger initially has {len(root_logger.handlers)} handlers ***")

for handler in root_logger.handlers[:]:
  root_logger.removeHandler(handler)
print("*** STARTUP: Removed existing handlers from root logger ***")

root_logger.setLevel(logging.INFO)

root_filter = LogRecordFilter()
if root_filter not in root_logger.filters:
  root_logger.addFilter(root_filter)

# Add JSON formatter handler for stdout
json_handler = logging.StreamHandler(sys.stdout)
json_handler.setFormatter(JsonFormatter())
root_logger.addHandler(json_handler)
print("*** STARTUP: Added JSON formatter handler to root logger ***")

# Create a global class logger
_static_logger = logging.getLogger("Logger")
_static_logger.setLevel(logging.INFO)
_static_logger.addFilter(LogRecordFilter())

# Define the instance logger class
class Logger:
  """Instance logger for module-specific logging."""

  def __init__(self, name):
    try:
      dirname = os.path.dirname(name)
      filename = os.path.split(name)[1]
      folder = os.path.split(dirname)[1] if dirname else "root"
      module_name = f"{folder}/{filename}"
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
    extra = kwargs.get("extra", {})
    kwargs["extra"] = _add_default_fields(extra)
    self.logger.info(msg, *args, **kwargs)

  def error(self, msg, *args, **kwargs):
    extra = kwargs.get("extra", {})
    kwargs["extra"] = _add_default_fields(extra)
    self.logger.error(msg, *args, **kwargs)

  def warning(self, msg, *args, **kwargs):
    extra = kwargs.get("extra", {})
    kwargs["extra"] = _add_default_fields(extra)
    self.logger.warning(msg, *args, **kwargs)

  def debug(self, msg, *args, **kwargs):
    extra = kwargs.get("extra", {})
    kwargs["extra"] = _add_default_fields(extra)
    self.logger.debug(msg, *args, **kwargs)

  def critical(self, msg, *args, **kwargs):
    extra = kwargs.get("extra", {})
    kwargs["extra"] = _add_default_fields(extra)
    self.logger.critical(msg, *args, **kwargs)

  def exception(self, msg, *args, **kwargs):
    extra = kwargs.get("extra", {})
    kwargs["extra"] = _add_default_fields(extra)
    self.logger.exception(msg, *args, **kwargs)

# Define static methods at module level
def info(msg, *args, **kwargs):
  """Static info logger."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
  """Static error logger."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.error(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
  """Static warning logger."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.warning(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
  """Static debug logger."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.debug(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
  """Static critical logger."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.critical(msg, *args, **kwargs)

def exception(msg, *args, **kwargs):
  """Static exception logger."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.exception(msg, *args, **kwargs)

Logger.info = staticmethod(info)
Logger.error = staticmethod(error)
Logger.warning = staticmethod(warning)
Logger.debug = staticmethod(debug)
Logger.critical = staticmethod(critical)
Logger.exception = staticmethod(exception)
