# Copyright 2025
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

"""Common monitoring middleware components for request tracking and metrics."""

import time
import uuid
import logging
import re
from fastapi import Request, Response
from fastapi.routing import APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional
from prometheus_client import (
  Counter,
  Histogram,
  generate_latest,
  CONTENT_TYPE_LATEST
)

# Import context variables and filter from logging_handler
try:
  from common.utils.logging_handler import (
    request_id_var, trace_var, session_id_var, debug_context_vars
  )
  # Debug the imported context vars
  print(f"*** STARTUP: middleware.py imported context vars from logging_handler ***")
  print(f"*** STARTUP: middleware.py request_id_var ID: {id(request_id_var)} ***")
  print(f"*** STARTUP: middleware.py trace_var ID: {id(trace_var)} ***")
  print(f"*** STARTUP: middleware.py session_id_var ID: {id(session_id_var)} ***")
except ImportError as e:
  # Only define these here if logging_handler import fails
  import contextvars
  print(f"*** STARTUP: Import from logging_handler failed: {e} ***")
  print("*** STARTUP: Defining local context vars ***")
  request_id_var = contextvars.ContextVar("request_id", default="-")
  trace_var = contextvars.ContextVar("trace", default="-")
  session_id_var = contextvars.ContextVar("session_id", default="-")
  print(f"*** STARTUP: middleware.py created local request_id_var ID: {id(request_id_var)} ***")
  
  # Define a debug helper function since import failed
  def debug_context_vars():
    """Print current context variable values for debugging."""
    print(f"DEBUG HELPER (middleware): Current context variable values:")
    print(f"  request_id_var (id={id(request_id_var)}): {request_id_var.get()}")
    print(f"  trace_var (id={id(trace_var)}): {trace_var.get()}")
    print(f"  session_id_var (id={id(session_id_var)}): {session_id_var.get()}")
    return {
      "request_id": request_id_var.get(), 
      "trace": trace_var.get(), 
      "session_id": session_id_var.get()
    }

try:
  from common.config import PROJECT_ID
except (ImportError, AttributeError):
  PROJECT_ID = "unknown-project"

try:
  from common.utils.logging_handler import Logger
except ImportError:
  Logger = None  # Will handle in _get_logger

# Default metrics for HTTP requests
REQUEST_COUNT = Counter(
  "fastapi_request_count", "FastAPI Request Count",
  ["app_name", "method", "endpoint", "http_status"]
)

REQUEST_LATENCY = Histogram(
  "fastapi_request_latency_seconds", "Request latency",
  ["app_name", "method", "endpoint"]
)

ERROR_COUNT = Counter(
  "fastapi_error_count", "FastAPI Error Count",
  ["app_name", "method", "endpoint", "error_type"]
)

class RequestTrackingMiddleware(BaseHTTPMiddleware):
  """Middleware to inject request_id and trace into logs and track requests.
  
  This middleware handles:
  1. Request ID generation or propagation
  2. Request tracing
  3. Logging instrumentation with request context
  4. Basic request metrics (optional)
  """

  # Regex to extract the trace ID from X-Cloud-Trace-Context
  TRACE_CONTEXT_RE = re.compile(r"([a-f0-9]{32})/([0-9]+)(?:;o=([0-9]+))?")

  def __init__(
      self,
      app,
      project_id: str = None,
      service_name: str = "service",
      collect_metrics: bool = False,
      request_count_metric: Optional[Counter] = None,
      request_latency_metric: Optional[Histogram] = None,
      error_count_metric: Optional[Counter] = None
  ):
    """Initialize the middleware with configuration options.
    
    Args:
      app: The FastAPI application
      project_id: Google Cloud project ID for trace context (if None,
                  attempts to get from common.config)
      service_name: Name of the service (used for metrics)
      collect_metrics: Whether to collect Prometheus metrics
      request_count_metric: Optional custom Counter for request counts
      request_latency_metric: Optional custom Histogram for request latency
      error_count_metric: Optional custom Counter for error counts
    """
    super().__init__(app)

    if project_id is None:
      project_id = PROJECT_ID

    self.project_id = project_id
    self.service_name = service_name
    self.collect_metrics = collect_metrics
    self.request_count = request_count_metric or REQUEST_COUNT
    self.request_latency = request_latency_metric or REQUEST_LATENCY
    self.error_count = error_count_metric or ERROR_COUNT
    self.logger = self._get_logger()
    
    # Debug the context vars in the constructor
    print(f"DEBUG MIDDLEWARE: Constructor context vars for {service_name}:")
    print(f"  request_id_var (id={id(request_id_var)}): {request_id_var.get()}")
    print(f"  trace_var (id={id(trace_var)}): {trace_var.get()}")
    print(f"  session_id_var (id={id(session_id_var)}): {session_id_var.get()}")

  def _get_logger(self):
    """Get the logger for the middleware."""
    if Logger is not None:
      return Logger.get_logger(__file__)
    return logging.getLogger(__name__)

  async def dispatch(self, request: Request, call_next):

    # Debug current context vars at start of request
    # In RequestTrackingMiddleware.dispatch method, add these lines at the beginning:
    print(f"==== REQUEST START: {request.url.path} ====")
    print(f"Headers: X-Request-ID={request.headers.get('X-Request-ID')}, X-Cloud-Trace-Context={request.headers.get('X-Cloud-Trace-Context')}")
    print(f"DEBUG MIDDLEWARE: Start of request context vars")
    debug_context_vars()
    
    # Capture start time for latency measurement
    start_time = time.time()

    # Get or generate request ID
    # The UI front end is expected to generate
    # this X-Request-ID, if not present, generate a service level uuid
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
      request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    print(f"DEBUG MIDDLEWARE: Using request_id: {request_id}")

    # Capture the trace ID from the ingress/GCLB
    trace_id = None
    cloud_trace_context = request.headers.get("X-Cloud-Trace-Context")
    if cloud_trace_context:
      match = self.TRACE_CONTEXT_RE.match(cloud_trace_context)
      if match:
        trace_id = match.group(1)  # Extract the 32-hex trace ID
        print(f"DEBUG MIDDLEWARE: Extracted trace_id from headers: {trace_id}")

    # Determine the ID to use for the trace context string
    # Prioritize the actual trace ID if available
    trace_id_for_context = trace_id if trace_id else request_id
    trace = f"projects/{self.project_id}/traces/{trace_id_for_context}"
    request.state.trace = trace
    print(f"DEBUG MIDDLEWARE: Set trace: {trace}")

    # Add session_id if available
    session_id = request.headers.get("X-Session-ID", "-")
    request.state.session_id = session_id
    print(f"DEBUG MIDDLEWARE: Set session_id: {session_id}")

    request.state.start_time = start_time

    # Set the context variables for this request
    print(f"DEBUG MIDDLEWARE: About to set context vars:")
    print(f"  request_id_var ID: {id(request_id_var)}")
    print(f"  request_id: {request_id}")
    token_request_id = request_id_var.set(request_id)
    token_trace = trace_var.set(trace)
    token_session_id = session_id_var.set(session_id)
    
    # Debug context vars after setting
    print(f"DEBUG MIDDLEWARE: After setting context vars:")
    print(f"  request_id_var.get(): {request_id_var.get()}")
    print(f"  trace_var.get(): {trace_var.get()}")
    print(f"  session_id_var.get(): {session_id_var.get()}")

    # Add debugging to verify context variables are set correctly
    self.logger.debug(
      "Context variables set in middleware",
      extra={
        "debug_request_id": request_id,
        "debug_trace": trace,
        "debug_session_id": session_id,
        "context_request_id": request_id_var.get(),
        "context_trace": trace_var.get(),
        "context_session_id": session_id_var.get(),
      }
    )

    try:
      # Log before processing
      print(f"DEBUG MIDDLEWARE: Before calling next middleware/handler")
      debug_context_vars()
      
      #debug
      print(f"==== CONTEXT BEFORE REQUEST: request_id={request_id_var.get()}, trace={trace_var.get()} ====")

      # Process the request
      response = await call_next(request)

      print(f"==== CONTEXT AFTER REQUEST: request_id={request_id_var.get()}, trace={trace_var.get()} ====")
      
      # Log after processing 
      print(f"DEBUG MIDDLEWARE: After calling next middleware/handler")
      debug_context_vars()

      # Calculate request metrics
      request_latency = time.time() - start_time
      method = request.method
      path = request.url.path

      # Collect metrics if enabled
      if self.collect_metrics:
        self.request_latency.labels(
          self.service_name, method, path
        ).observe(request_latency)

        self.request_count.labels(
          self.service_name, method, path, response.status_code
        ).inc()

      # Add request ID to response headers
      response.headers["X-Request-ID"] = request_id

      # Log request completion (debug level) and include ids
      self.logger.debug(
        "Request processed",
        extra={
          "metric_type": "request",
          "method": method,
          "path": path,
          "status_code": response.status_code,
          "duration_ms": round(request_latency * 1000, 2)
        }
      )

      return response
    except Exception as exc:
      # Handle and log exceptions
      error_type = type(exc).__name__

      if self.collect_metrics:
        self.error_count.labels(
          self.service_name, request.method, request.url.path, error_type
        ).inc()

      self.logger.error(
        "Request error",
        extra={
          "metric_type": "request_error",
          "method": request.method,
          "path": request.url.path,
          "error_type": error_type,
          "error_message": str(exc)
        }
      )

      raise
    finally:
      # Debug context variables before reset
      print(f"DEBUG MIDDLEWARE: Before resetting context vars:")
      debug_context_vars()
      
      self.logger.debug(
        "Context variables before reset",
        extra={
          "final_request_id": request_id_var.get(),
          "final_trace": trace_var.get(),
          "final_session_id": session_id_var.get(),
        }
      )

      # Reset context variables
      print(f"DEBUG MIDDLEWARE: Resetting context vars with tokens:")
      print(f"  token_request_id: {token_request_id}")
      request_id_var.reset(token_request_id)
      trace_var.reset(token_trace)
      session_id_var.reset(token_session_id)
      
      # Debug after reset
      print(f"DEBUG MIDDLEWARE: After resetting context vars:")
      debug_context_vars()


class PrometheusMiddleware(BaseHTTPMiddleware):
  """Middleware to collect Prometheus metrics for all requests."""

  def __init__(self, app, service_name: str = "service"):
    """Initialize the middleware.
    
    Args:
      app: The FastAPI application
      service_name: Name of the service to use in metrics
    """
    super().__init__(app)
    self.service_name = service_name

  async def dispatch(self, request: Request, call_next):
    start_time = time.time()
    method = request.method
    path = request.url.path

    try:
      response = await call_next(request)
      request_latency = time.time() - start_time

      REQUEST_LATENCY.labels(
        self.service_name, method, path
      ).observe(request_latency)

      REQUEST_COUNT.labels(
        self.service_name, method, path, response.status_code
      ).inc()

      return response
    except Exception as exc:
      error_type = type(exc).__name__
      ERROR_COUNT.labels(
        self.service_name, method, path, error_type
      ).inc()

      raise

def create_metrics_router() -> APIRouter:
  """Creates a router with the /metrics endpoint for Prometheus scraping.
  
  Returns:
    APIRouter: Router with /metrics endpoint configured
  """
  metrics_router = APIRouter(tags=["Metrics"])

  @metrics_router.get("/metrics")
  async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

  return metrics_router

def get_request_context(args) -> tuple:
  """Extract request_id, trace and session_id from request if available.
  
  Args:
    args: Arguments passed to the decorated function
      
  Returns:
    tuple: request_id, trace, session_id extracted from arguments or defaults
  """
  # Debug current context vars
  print(f"DEBUG MIDDLEWARE: get_request_context called")
  debug_context_vars()
  
  # First check context vars (for use outside of request handlers)
  request_id = request_id_var.get()
  trace = trace_var.get()
  session_id = session_id_var.get()
  
  print(f"DEBUG MIDDLEWARE: get_request_context initial values:")
  print(f"  request_id: {request_id}")
  print(f"  trace: {trace}")
  print(f"  session_id: {session_id}")

  # Then try to extract from request if available
  for arg in args:
    if hasattr(arg, "state"):
      request_id = getattr(arg.state, "request_id", request_id)
      trace = getattr(arg.state, "trace", trace)
      session_id = getattr(arg.state, "session_id", session_id)
      print(f"DEBUG MIDDLEWARE: Found request state, extracted values:")
      print(f"  request_id: {request_id}")
      print(f"  trace: {trace}")
      print(f"  session_id: {session_id}")
      break

  print(f"DEBUG MIDDLEWARE: get_request_context returning:")
  print(f"  request_id: {request_id}")
  print(f"  trace: {trace}")
  print(f"  session_id: {session_id}")
  return request_id, trace, session_id


# Debug endpoint for testing context variables and logging
def create_debug_router() -> APIRouter:
  """Creates a router with debug endpoints for troubleshooting.
  
  Returns:
    APIRouter: Router with debug endpoints
  """
  debug_router = APIRouter(tags=["Debug"])
  
  @debug_router.get("/debug/context-vars")
  async def debug_context_vars_endpoint(request: Request):
    """Endpoint to check the current state of context variables"""
    # Get the context variables directly
    ctx_request_id = request_id_var.get()
    ctx_trace = trace_var.get()
    ctx_session_id = session_id_var.get()
    
    # Get values from request state
    req_request_id = getattr(request.state, "request_id", "-")
    req_trace = getattr(request.state, "trace", "-") 
    req_session_id = getattr(request.state, "session_id", "-")
    
    # Create response
    response = {
      "context_vars": {
        "request_id_var": ctx_request_id,
        "trace_var": ctx_trace,
        "session_id_var": ctx_session_id,
        "request_id_var_id": str(id(request_id_var)),
        "trace_var_id": str(id(trace_var)),
        "session_id_var_id": str(id(session_id_var))
      },
      "request_state": {
        "request_id": req_request_id,
        "trace": req_trace,
        "session_id": req_session_id
      },
      "headers": {
        "x-request-id": request.headers.get("X-Request-ID", "-"),
        "x-cloud-trace-context": request.headers.get("X-Cloud-Trace-Context", "-"),
        "x-session-id": request.headers.get("X-Session-ID", "-")
      }
    }
    
    # Also log these values
    logger = logging.getLogger("debug.context_vars")
    logger.info(
      "Debug context vars endpoint called",
      extra={
        "context_request_id": ctx_request_id,
        "context_trace": ctx_trace,
        "context_session_id": ctx_session_id,
        "request_state_request_id": req_request_id,
        "request_state_trace": req_trace,
        "request_state_session_id": req_session_id
      }
    )
    
    return response
  
  @debug_router.get("/debug/log-check")
  async def debug_log_check(request: Request):
    """Endpoint to test logging with context variables"""
    logger = logging.getLogger("debug.log_check")
    
    # Get current context values
    current_request_id = request_id_var.get()
    current_trace = trace_var.get()
    current_session_id = session_id_var.get()
    
    # Log with explicit extras
    logger.info(
      "Debug log check",
      extra={
        "test_request_id": getattr(request.state, "request_id", "NOT_SET"),
        "test_trace": getattr(request.state, "trace", "NOT_SET"),
        "test_session_id": getattr(request.state, "session_id", "NOT_SET"),
        "context_request_id": current_request_id,
        "context_trace": current_trace,
        "context_session_id": current_session_id,
      }
    )
    
    # Create and log with a new Logger instance
    custom_logger = Logger.get_logger("debug.custom_logger_check")
    custom_logger.info(
      "Custom logger check",
      extra={
        "custom_logger": True
      }
    )
    
    return {
      "message": "Debug log created",
      "request_id": current_request_id,
      "trace": current_trace,
      "session_id": current_session_id,
      "request_state_values": {
        "request_id": getattr(request.state, "request_id", "NOT_SET"),
        "trace": getattr(request.state, "trace", "NOT_SET"),
        "session_id": getattr(request.state, "session_id", "NOT_SET"),
      }
    }
  