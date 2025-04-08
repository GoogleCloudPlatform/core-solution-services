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

"""Class and methods for structured logging with Cloud Logging support."""

import json
import logging
import os
import sys
import traceback
import datetime
from common.config import CLOUD_LOGGING_ENABLED, SERVICE_NAME, CONTAINER_NAME

# Get log level from environment, default to INFO
LOG_LEVEL_NAME = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)

# Initialize Cloud Logging if enabled
if CLOUD_LOGGING_ENABLED:
  try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    print("*** STARTUP: Initialized Cloud Logging client ***")
  except Exception as e:
    print(f"*** STARTUP: Failed to initialize Cloud Logging client: {e} ***")
    print("*** STARTUP: Falling back to standard logging ***")
    client = None
else:
  client = None

# Create a filter to add missing fields
class LogRecordFilter(logging.Filter):
  """Filter to ensure required fields are present in log records."""

  def filter(self, record):
    # Add default values for required fields if they don"t exist
    if not hasattr(record, "request_id"):
      record.request_id = "-"
    if not hasattr(record, "trace"):
      record.trace = "-"
    if not hasattr(record, "session_id"):
      record.session_id = "-"

    return True

# Custom JSON encoder that handles non-serializable objects
class SafeJsonEncoder(json.JSONEncoder):
  """JSON encoder that safely handles non-serializable objects."""

  def default(self, obj):
    try:
      return super().default(obj)
    except TypeError:
      # For objects that can"t be serialized, convert to string
      return str(obj)

# Helper function to add default fields
def _add_default_fields(extra=None):
  """Add default fields to extra dictionary."""
  if extra is None:
    extra = {}

  # Add default values for standard fields
  if "request_id" not in extra:
    extra["request_id"] = "-"
  if "trace" not in extra:
    extra["trace"] = "-"
  if "session_id" not in extra:
    extra["session_id"] = "-"

  # Store all additional fields in extras dictionary
  extras = {k: v for k, v in extra.items()
           if k not in ["request_id", "trace", "session_id"]}
  if extras:
    extra["extras"] = extras

  return extra

# Custom JSON formatter for structured logging
class JsonFormatter(logging.Formatter):
  """JSON formatter for structured logging that preserves extra fields."""

  def format(self, record):
    # Generate ISO-8601 timestamp compatible with Cloud Logging
    timestamp = datetime.datetime.fromtimestamp(record.created).isoformat() + "Z"

    # Build basic log record info
    log_entry = {
      "timestamp": timestamp,
      "message": record.getMessage(),
      "severity": record.levelname,
      "logger": record.name,
      "file": record.pathname,
      "line": record.lineno,
      "function": record.funcName,
      "service": SERVICE_NAME or CONTAINER_NAME or "unknown-service"
    }

    # Add context fields with standardized naming
    log_entry["request_id"] = getattr(record, "request_id", "-")
    log_entry["trace"] = getattr(record, "trace", "-")
    log_entry["session_id"] = getattr(record, "session_id", "-")

    # Properly format trace for Google Cloud Logging
    trace_value = log_entry["trace"]
    if trace_value != "-":
      if trace_value.startswith("projects/"):
        # Trace is already in full format (from middleware)
        log_entry["logging.googleapis.com/trace"] = trace_value
      else:
        # Just use the trace ID as provided
        log_entry["logging.googleapis.com/trace"] = trace_value

    # Add null values instead of dash placeholders for cleaner JSON
    for field in ["request_id", "trace", "session_id"]:
      if log_entry[field] == "-":
        log_entry[field] = None

    # Add any extras fields from the record
    extras = getattr(record, "extras", {})
    if isinstance(extras, dict):
      for key, value in extras.items():
        if key not in log_entry:
          log_entry[key] = value

    # Process any nested fields in extras to bring them up to the top level
    if "extras" in log_entry and isinstance(log_entry["extras"], dict):
      for nested_key, nested_value in log_entry["extras"].items():
        if nested_key not in log_entry:
          log_entry[nested_key] = nested_value
      # remove the original extras to avoid duplication
      del log_entry["extras"]

    # Look for specific metric fields directly on the record
    standard_attributes = [
      "args", "created", "exc_info", "exc_text", "filename", 
      "funcName", "levelname", "levelno", "lineno", "module", 
      "msecs", "msg", "name", "pathname", "process", 
      "processName", "relativeCreated", "stack_info", 
      "thread", "threadName"
    ]

    for attr_name in dir(record):
      # Skip private attributes, methods, and already-processed fields
      if (not attr_name.startswith("__") and
          not callable(getattr(record, attr_name)) and
          attr_name not in log_entry and
          attr_name not in standard_attributes):
        log_entry[attr_name] = getattr(record, attr_name)

    # Add exception info if present
    if record.exc_info:
      exception_data = {
        "type": record.exc_info[0].__name__,
        "message": str(record.exc_info[1]),
        "traceback": traceback.format_exception(*record.exc_info)
      }
      log_entry["exception"] = exception_data

    # Return JSON string, handling non-serializable objects
    try:
      return json.dumps(log_entry, cls=SafeJsonEncoder)
    except Exception as e:
      # Fallback in case JSON serialization fails completely
      return json.dumps({
        "timestamp": timestamp,
        "severity": "ERROR",
        "logger": "logging_handler",
        "message": f"Failed to serialize log: {str(e)}",
        "original_message": record.getMessage()
      })

# Force reconfiguration of root logger by removing existing handlers
root_logger = logging.getLogger()
print(f"*** STARTUP: Root logger initially has {len(root_logger.handlers)} handlers ***")

for handler in root_logger.handlers[:]:
  root_logger.removeHandler(handler)
print("*** STARTUP: Removed existing handlers from root logger ***")

# Set log level from environment
root_logger.setLevel(LOG_LEVEL)

# Add filter to root logger
root_filter = LogRecordFilter()
if root_filter not in root_logger.filters:
  root_logger.addFilter(root_filter)

# Add handlers to root logger
if CLOUD_LOGGING_ENABLED and client:
  # If Cloud Logging is enabled, use its handler
  cloud_handler = client.get_default_handler()
  cloud_handler.setFormatter(JsonFormatter())
  root_logger.addHandler(cloud_handler)
  print("*** STARTUP: Added Cloud Logging handler to root logger ***")
else:
  # Otherwise use standard JSON output to stdout
  json_handler = logging.StreamHandler(sys.stdout)
  json_handler.setFormatter(JsonFormatter())
  root_logger.addHandler(json_handler)
  print("*** STARTUP: Added JSON formatter handler to root logger ***")

print(f"*** STARTUP: Initialized structured logging with level: {LOG_LEVEL_NAME} ***")
print(f"*** STARTUP: Structured fields enabled: request_id, session_id, trace ***")

# Create a global class logger
_static_logger = logging.getLogger("Logger")
_static_logger.setLevel(LOG_LEVEL)
_static_logger.addFilter(LogRecordFilter())

# Define the instance logger class
class Logger:
  """Instance logger for module-specific logging with structured output."""

  def __init__(self, name):
    try:
      dirname = os.path.dirname(name)
      filename = os.path.split(name)[1]
      folder = os.path.split(dirname)[1] if dirname else "root"
      module_name = f"{folder}/{filename}"
    except (IndexError, AttributeError):
      module_name = str(name)

    self.logger = logging.getLogger(module_name)
    self.logger.setLevel(LOG_LEVEL)
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
