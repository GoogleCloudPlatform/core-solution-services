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
import traceback
import datetime

# Import context variables
from common.utils.context_vars import (
  request_id_var, trace_var, session_id_var
)

try:
  from common.config import (
    CLOUD_LOGGING_ENABLED, SERVICE_NAME, CONTAINER_NAME, PROJECT_ID
  )
except ImportError:
  # Default values if config isn't available
  CLOUD_LOGGING_ENABLED = False
  SERVICE_NAME = os.environ.get("SERVICE_NAME", "unknown-service")
  CONTAINER_NAME = os.environ.get("CONTAINER_NAME", "unknown-container")
  PROJECT_ID = os.environ.get("PROJECT_ID", "unknown-project")

# Get log level from environment, default to INFO
LOG_LEVEL_NAME = os.environ.get("LOG_LEVEL", "INFO").upper()
LOG_LEVEL = getattr(logging, LOG_LEVEL_NAME, logging.INFO)

# Custom JSON encoder that handles non-serializable objects
class SafeJsonEncoder(json.JSONEncoder):
  """JSON encoder that safely handles non-serializable objects."""

  def default(self, o):
    if isinstance(o, (datetime.datetime, datetime.date)):
      return o.isoformat()
    if hasattr(o, "__dict__"):
      return o.__dict__
    return str(o)

class LogRecordFilter(logging.Filter):
  """Filter to ensure context variables are included in log records."""

  def filter(self, record):
    # Get current context variables - directly from context vars
    # which ensures we get the right values even in async contexts
    record.request_id = request_id_var.get()
    record.trace = trace_var.get()
    record.session_id = session_id_var.get()

    # Make sure we have values (not just defaults)
    if record.request_id == "-":
      record.request_id = None
    if record.trace == "-":
      record.trace = None
    if record.session_id == "-":
      record.session_id = None

    return True

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
  """JSON formatter for structured logging that preserves context variables."""

  def format(self, record):
    # Generate ISO-8601 timestamp compatible with Cloud Logging
    timestamp = datetime.datetime.fromtimestamp(
      record.created).isoformat() + "Z"

    # Always get context vars directly to ensure accurate values
    ctx_request_id = request_id_var.get()
    ctx_trace = trace_var.get()
    ctx_session_id = session_id_var.get()

    # Use context vars as primary source, fallback to record attributes
    request_id = getattr(record, "request_id", ctx_request_id)
    trace = getattr(record, "trace", ctx_trace)
    session_id = getattr(record, "session_id", ctx_session_id)

    # Apply defaults
    if request_id == "-":
      request_id = None
    if trace == "-":
      trace = None
    if session_id == "-":
      session_id = None

    # Build core log entry with essential fields only
    log_entry = {
      "timestamp": timestamp,
      "severity": record.levelname,
      "message": record.getMessage(),
      "service": SERVICE_NAME or CONTAINER_NAME or "unknown-service",
      "logger": record.name,
      "file": record.pathname,
      "function": record.funcName,
      "line": record.lineno,
      "request_id": request_id,
      "trace": trace,
      "session_id": session_id
    }

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

    # Return JSON string with simplified error handling
    try:
      return json.dumps(log_entry, cls=SafeJsonEncoder)
    except Exception as exc:
      error_msg = {
        "timestamp": timestamp,
        "severity": "ERROR",
        "message": f"Log serialization error: {str(exc)}",
        "service": SERVICE_NAME or CONTAINER_NAME or "unknown-service",
        "logger": "logging_handler",
        "original_message": str(record.getMessage())
      }
      print(f"ERROR IN LOGGER: {json.dumps(error_msg)}")
      return json.dumps(error_msg)
