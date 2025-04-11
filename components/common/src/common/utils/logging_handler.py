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
import contextvars
from common.config import CLOUD_LOGGING_ENABLED, SERVICE_NAME, CONTAINER_NAME

# Define context variables at module level to be used across the application
request_id_var = contextvars.ContextVar("request_id", default="-")
trace_var = contextvars.ContextVar("trace", default="-")
session_id_var = contextvars.ContextVar("session_id", default="-")

# Adding debugging to track the context variables instances
cv_instance_id = id(request_id_var)
print(f"*** STARTUP: logging_handler.py created request_id_var with ID: {cv_instance_id} ***")
print(f"*** STARTUP: trace_var ID: {id(trace_var)} ***")
print(f"*** STARTUP: session_id_var ID: {id(session_id_var)} ***")

# Get log level from environment, default to INFO
LOG_LEVEL_NAME = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)

# Initialize Cloud Logging if enabled
if CLOUD_LOGGING_ENABLED:
  try:
    import google.cloud.logging
    client = google.cloud.logging.Client()
    print("*** STARTUP: Initialized Cloud Logging client ***")
  except (ImportError, google.cloud.exceptions.GoogleCloudError) as e:
    print(f"*** STARTUP: Failed to initialize Cloud Logging client: {e} ***")
    print("*** STARTUP: Falling back to standard logging ***")
    client = None
  except Exception as e:
    print(f"*** STARTUP: Unexpected error with Cloud Logging client: {e} ***")
    print("*** STARTUP: Falling back to standard logging ***")
    client = None
    raise
else:
  client = None


# Create a single filter for the whole application
class LogRecordFilter(logging.Filter):
  """Filter to ensure required fields are present in log records."""

  def filter(self, record):
    """Add request context to the log record."""
    # Debug logging to trace filter execution - remove in production
    print(f"DEBUG LOGGER: Filtering record: name={record.name}")
    
    # Debug - show current context variable values
    print(f"DEBUG LOGGER: Context var values at filter time:")
    print(f"  request_id_var: {request_id_var.get()}")
    print(f"  trace_var: {trace_var.get()}")
    print(f"  session_id_var: {session_id_var.get()}")
    
    # Debug - show current record values
    print(f"DEBUG LOGGER: Initial record values:")
    print(f"  request_id: {getattr(record, 'request_id', '-')}")
    print(f"  trace: {getattr(record, 'trace', '-')}")
    print(f"  session_id: {getattr(record, 'session_id', '-')}")

    # Only set values if they're not already present
    if not hasattr(record, "request_id") or record.request_id == "-":
      # Try to get from context vars
      ctx_request_id = request_id_var.get()
      record.request_id = ctx_request_id if ctx_request_id != "-" else None
      print(f"DEBUG LOGGER: Set request_id to: {record.request_id}")

    if not hasattr(record, "trace") or record.trace == "-":
      # Try to get from context vars
      ctx_trace = trace_var.get()
      record.trace = ctx_trace if ctx_trace != "-" else None
      print(f"DEBUG LOGGER: Set trace to: {record.trace}")

    if not hasattr(record, "session_id") or record.session_id == "-":
      # Try to get from context vars
      ctx_session_id = session_id_var.get()
      record.session_id = ctx_session_id if ctx_session_id != "-" else None
      print(f"DEBUG LOGGER: Set session_id to: {record.session_id}")

    # Debug final values
    print(f"DEBUG LOGGER: Final record values:")
    print(f"  request_id: {getattr(record, 'request_id', '-')}")
    print(f"  trace: {getattr(record, 'trace', '-')}")
    print(f"  session_id: {getattr(record, 'session_id', '-')}")

    return True

# Create a single instance of the filter for the entire application
log_record_filter = LogRecordFilter()

# Custom JSON encoder that handles non-serializable objects
class SafeJsonEncoder(json.JSONEncoder):
  """JSON encoder that safely handles non-serializable objects."""

  def default(self, o):
    # Handle common types that are problematic in JSON
    if isinstance(o, (datetime.datetime, datetime.date)):
      return o.isoformat()
    if hasattr(o, "__dict__"):
      return o.__dict__
    # Fall back to string representation for anything else
    return str(o)

# Helper function to add default fields
def _add_default_fields(extra=None):
  """Add default fields to extra dictionary."""
  if extra is None:
    extra = {}

  # Debug - show current context variable values
  print(f"DEBUG LOGGER: _add_default_fields context var values:")
  print(f"  request_id_var: {request_id_var.get()}")
  print(f"  trace_var: {trace_var.get()}")
  print(f"  session_id_var: {session_id_var.get()}")

  # Set default fields only if not present
  for field in ["request_id", "trace", "session_id"]:
    if field not in extra:
      # Try to get from context vars first
      if field == "request_id":
        extra[field] = request_id_var.get()
      elif field == "trace":
        extra[field] = trace_var.get()
      elif field == "session_id":
        extra[field] = session_id_var.get()
      else:
        extra[field] = "-"

  print(f"DEBUG LOGGER: _add_default_fields result: {extra}")
  return extra

# Standard attributes to exclude when processing record.__dict__
STANDARD_ATTRIBUTES = {
  "args", "created", "exc_info", "exc_text", "filename", 
  "funcName", "levelname", "levelno", "lineno", "module", 
  "msecs", "msg", "name", "pathname", "process", 
  "processName", "relativeCreated", "stack_info", 
  "thread", "threadName", "request_id", "trace", "session_id"
}

# Custom JSON formatter for structured logging
class JsonFormatter(logging.Formatter):
  """JSON formatter for structured logging that preserves extra fields."""

  def format(self, record):
    # Generate ISO-8601 timestamp compatible with Cloud Logging
    timestamp = datetime.datetime.fromtimestamp(
      record.created).isoformat() + "Z"

    # Debug - show what values we have when formatting
    print(f"DEBUG LOGGER: JsonFormatter.format record values:")
    print(f"  request_id: {getattr(record, 'request_id', '-')}")
    print(f"  trace: {getattr(record, 'trace', '-')}")
    print(f"  session_id: {getattr(record, 'session_id', '-')}")

    # Build core log entry with essential fields only
    log_entry = {
      "timestamp": timestamp,
      "severity": record.levelname,
      "message": record.getMessage(),
      "service": SERVICE_NAME or CONTAINER_NAME or "unknown-service",
      "logger": record.name,
      "file": record.pathname,
      "function": record.funcName,
      "line": record.lineno
    }

    # Add request context fields but use null instead of dashes
    for field in ["request_id", "trace", "session_id"]:
      value = getattr(record, field, "-")
      log_entry[field] = None if value == "-" else value

    # Handle Cloud Logging trace format
    if log_entry["trace"]:
      if isinstance(log_entry["trace"], str) and log_entry[
        "trace"].startswith("projects/"):
        log_entry["logging.googleapis.com/trace"] = log_entry["trace"]
      elif log_entry["trace"] != "-" and log_entry["trace"] is not None:
        log_entry["logging.googleapis.com/trace"] = log_entry["trace"]

    # Add exception info if present
    if record.exc_info:
      log_entry["exception"] = {
        "type": record.exc_info[0].__name__,
        "message": str(record.exc_info[1]),
        "traceback": traceback.format_exception(*record.exc_info)
      }

    # Process additional fields in a single pass from record.__dict__
    # Skip standard attributes and already processed fields
    for key, value in record.__dict__.items():
      if (key not in STANDARD_ATTRIBUTES and
          key not in log_entry and
          not key.startswith("_") and
          not callable(value)):
        log_entry[key] = value

    # Add extras content if present
    extras = getattr(record, "extras", {})
    if isinstance(extras, dict):
      for key, value in extras.items():
        if key not in log_entry:
          log_entry[key] = value

    # Debug - show final log entry before serialization
    print(f"DEBUG LOGGER: Final log_entry keys: {list(log_entry.keys())}")
    print(f"DEBUG LOGGER: Final trace value: {log_entry.get('trace')}")

    # Return JSON string with simplified error handling
    try:
      return json.dumps(log_entry, cls=SafeJsonEncoder)
    except TypeError as exc:
      error_msg = {
        "timestamp": timestamp,
        "severity": "ERROR",
        "message": f"Log serialization error: {type(exc).__name__}: {str(exc)}",
        "service": SERVICE_NAME or CONTAINER_NAME or "unknown-service",
        "logger": "logging_handler",
        "original_message": str(record.getMessage())
      }
      print(error_msg)
      raise
    except ValueError as exc:
      error_msg = {
        "timestamp": timestamp,
        "severity": "ERROR",
        "message": f"JSON value error: {type(exc).__name__}: {str(exc)}",
        "service": SERVICE_NAME or CONTAINER_NAME or "unknown-service",
        "logger": "logging_handler"
      }
      print(error_msg)
      raise
    except Exception as exc:
      error_msg = {
        "timestamp": timestamp,
        "severity": "ERROR",
        "message": f"Unexpected error in log formatting: {str(exc)}",
        "service": SERVICE_NAME or CONTAINER_NAME or "unknown-service",
        "logger": "logging_handler"
      }
      print(error_msg)
      raise


# Force reconfiguration of root logger by removing existing handlers
root_logger = logging.getLogger()
print("*** STARTUP: Root logger initially has"
      f" {len(root_logger.handlers)} handlers ***")

for handler in root_logger.handlers[:]:
  root_logger.removeHandler(handler)
print("*** STARTUP: Removed existing handlers from root logger ***")

# Set log level from environment
root_logger.setLevel(LOG_LEVEL)

# Add filter to root logger - use the single instance created above
if log_record_filter not in root_logger.filters:
  root_logger.addFilter(log_record_filter)
  print("*** STARTUP: Added LogRecordFilter to root logger ***")
  print("*** STARTUP: Root logger filters: " +
        f"{[type(f).__name__ for f in root_logger.filters]} ***")

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

print("*** STARTUP: Initialized structured logging "
      f"with level: {LOG_LEVEL_NAME} ***")

# Create a global class logger
_static_logger = logging.getLogger("Logger")
_static_logger.setLevel(LOG_LEVEL)
# No need to add filter here as root logger already has it

# Cache for logger instances
_logger_cache = {}

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
    # No need to add filter here as root logger already has it

  @classmethod
  def get_logger(cls, name) -> logging.Logger:
    if name in _logger_cache:
      return _logger_cache[name]

    logger_instance = cls(name)
    _logger_cache[name] = logger_instance.logger
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

# Debug helper function for testing context vars
def debug_context_vars():
  """Print current context variable values for debugging."""
  print(f"DEBUG HELPER: Current context variable values:")
  print(f"  request_id_var (id={id(request_id_var)}): {request_id_var.get()}")
  print(f"  trace_var (id={id(trace_var)}): {trace_var.get()}")
  print(f"  session_id_var (id={id(session_id_var)}): {session_id_var.get()}")
  return {
    "request_id": request_id_var.get(),
    "trace": trace_var.get(), 
    "session_id": session_id_var.get()
  }

# Expose necessary elements for importing
__all__ = ["Logger",
          "log_record_filter",
          "request_id_var",
          "trace_var",
          "session_id_var",
          "debug_context_vars"]
