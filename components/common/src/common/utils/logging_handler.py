"""Class and methods for structured logging with Cloud Logging support."""

import json
import logging
import os
import sys
import traceback
import datetime

# Import context variables
from common.utils.context_vars import (
  request_id_var, trace_var, session_id_var
)

# Try to import configuration
try:
  from common.config import (
    CLOUD_LOGGING_ENABLED, SERVICE_NAME, CONTAINER_NAME
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
    raise
else:
  client = None

# Custom JSON encoder that handles non-serializable objects
class SafeJsonEncoder(json.JSONEncoder):
  """JSON encoder that safely handles non-serializable objects."""

  def _boolstr(self, val):
    """Convert boolean values to lowercase strings."""
    if isinstance(val, bool):
      return str(val).lower()
    return val

  def default(self, o):
    # Convert boolean values to lowercase strings
    if isinstance(o, bool):
      return self._boolstr(o)
    if isinstance(o, (datetime.datetime, datetime.date)):
      return o.isoformat()
    if hasattr(o, "__dict__"):
      return o.__dict__
    return str(o)

  def encode(self, o):
    # Process dictionaries to convert any boolean values to lowercase strings
    if isinstance(o, dict):
      for key, value in o.items():
        if isinstance(value, bool):
          o[key] = self._boolstr(value)
    # Handle boolean values in lists
    elif isinstance(o, list):
      for i, item in enumerate(o):
        if isinstance(item, bool):
          o[i] = self._boolstr(item)

    # Call the parent encode method
    return super().encode(o)

class LogRecordFilter(logging.Filter):
  """Filter to ensure context variables are included in log records."""

  def filter(self, record):
    # Get current context variables directly from context vars
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

# Helper function to add default fields with context variable awareness
def _add_default_fields(extra=None):
  """Add default fields to extra dictionary.
  
  Gets context variables directly to ensure accurate values in async contexts.
  """
  if extra is None:
    extra = {}

  # Get current context variables
  ctx_request_id = request_id_var.get()
  ctx_trace = trace_var.get()
  ctx_session_id = session_id_var.get()

  # Only set if not already in extra
  if "request_id" not in extra and ctx_request_id != "-":
    extra["request_id"] = ctx_request_id
  if "trace" not in extra and ctx_trace != "-":
    extra["trace"] = ctx_trace
  if "session_id" not in extra and ctx_session_id != "-":
    extra["session_id"] = ctx_session_id

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

# Add filter to root logger
log_record_filter = LogRecordFilter()
if log_record_filter not in root_logger.filters:
  root_logger.addFilter(log_record_filter)
  print("*** STARTUP: Added LogRecordFilter to root logger ***")

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
    """Get a logger instance, using cache for efficiency."""
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
  """Static info logger with context awareness."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.info(msg, *args, **kwargs)

def error(msg, *args, **kwargs):
  """Static error logger with context awareness."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.error(msg, *args, **kwargs)

def warning(msg, *args, **kwargs):
  """Static warning logger with context awareness."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.warning(msg, *args, **kwargs)

def debug(msg, *args, **kwargs):
  """Static debug logger with context awareness."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.debug(msg, *args, **kwargs)

def critical(msg, *args, **kwargs):
  """Static critical logger with context awareness."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.critical(msg, *args, **kwargs)

def exception(msg, *args, **kwargs):
  """Static exception logger with context awareness."""
  extra = kwargs.get("extra", {})
  kwargs["extra"] = _add_default_fields(extra)
  _static_logger.exception(msg, *args, **kwargs)

# Attach static methods to Logger class
Logger.info = staticmethod(info)
Logger.error = staticmethod(error)
Logger.warning = staticmethod(warning)
Logger.debug = staticmethod(debug)
Logger.critical = staticmethod(critical)
Logger.exception = staticmethod(exception)

# Expose necessary elements
__all__ = ["Logger", "log_record_filter"]
