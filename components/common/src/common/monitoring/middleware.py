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
    request_id_var, trace_var, session_id_var
  )
  print("*** STARTUP: Successfully imported from logging_handler ***")
except ImportError as e:
  # Only define these here if logging_handler import fails
  import contextvars
  print(f"*** STARTUP: Import from logging_handler failed: {e} ***")
  print("*** STARTUP: Defining local context vars ***")
  request_id_var = contextvars.ContextVar("request_id", default="-")
  trace_var = contextvars.ContextVar("trace", default="-")
  session_id_var = contextvars.ContextVar("session_id", default="-")
  log_record_filter = None

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

  def _get_logger(self):
    """Get the logger for the middleware."""
    if Logger is not None:
      return Logger.get_logger(__file__)
    return logging.getLogger(__name__)

  async def dispatch(self, request: Request, call_next):
    # Capture start time for latency measurement
    start_time = time.time()

    # Get or generate request ID
    # The UI front end is expected to generate
    # this X-Request-ID, if not present, generate a service level uuid
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
      request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Capture the trace ID from the ingress/GCLB
    trace_id = None
    cloud_trace_context = request.headers.get("X-Cloud-Trace-Context")
    if cloud_trace_context:
      match = self.TRACE_CONTEXT_RE.match(cloud_trace_context)
      if match:
        trace_id = match.group(1)  # Extract the 32-hex trace ID

    # Determine the ID to use for the trace context string
    # Prioritize the actual trace ID if available
    trace_id_for_context = trace_id if trace_id else request_id
    trace = f"projects/{self.project_id}/traces/{trace_id_for_context}"
    request.state.trace = trace

    # Add session_id if available
    session_id = request.headers.get("X-Session-ID", "-")
    request.state.session_id = session_id

    request.state.start_time = start_time

    # Set the context variables for this request
    token_request_id = request_id_var.set(request_id)
    token_trace = trace_var.set(trace)
    token_session_id = session_id_var.set(session_id)

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
      # Process the request
      response = await call_next(request)

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
    except Exception as e:
      # Handle and log exceptions
      error_type = type(e).__name__

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
          "error_message": str(e)
        }
      )

      raise
    finally:
      # Debug context variables before reset
      self.logger.debug(
        "Context variables before reset",
        extra={
          "final_request_id": request_id_var.get(),
          "final_trace": trace_var.get(),
          "final_session_id": session_id_var.get(),
        }
      )

      # Reset context variables
      request_id_var.reset(token_request_id)
      trace_var.reset(token_trace)
      session_id_var.reset(token_session_id)

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
    except Exception as e:
      error_type = type(e).__name__
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
  # First check context vars (for use outside of request handlers)
  request_id = request_id_var.get()
  trace = trace_var.get()
  session_id = session_id_var.get()

  # Then try to extract from request if available
  for arg in args:
    if hasattr(arg, "state"):
      request_id = getattr(arg.state, "request_id", request_id)
      trace = getattr(arg.state, "trace", trace)
      session_id = getattr(arg.state, "session_id", session_id)
      break

  return request_id, trace, session_id
