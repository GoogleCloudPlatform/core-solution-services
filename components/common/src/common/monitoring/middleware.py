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
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from common.utils.logging_handler import Logger

# Import context variables from the centralized module
from common.utils.context_vars import (
  set_context, reset_context,AsyncContextPreserver
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
    **kwargs
  ):
    """Initialize the middleware with configuration options."""
    super().__init__(app)

    self.project_id = project_id
    self.service_name = service_name
    self.collect_metrics = collect_metrics
    # Get other metrics from kwargs if provided
    self.request_count = kwargs.get("request_count_metric")
    self.request_latency = kwargs.get("request_latency_metric")
    self.error_count = kwargs.get("error_count_metric")

    # Set up logger
    self.logger = self._get_logger()

  def _get_logger(self):
    """Get the logger for the middleware."""
    try:
      return Logger.get_logger(__file__)
    except ImportError:
      return logging.getLogger(__name__)

  async def dispatch(self, request: Request, call_next):
    """Process request, adds tracking IDs, and collects metrics.
    
    This method carefully manages context propagation across await boundaries.
    """
    # Debug current context vars at start of request
    #self.logger.debug(f"Request started: {request.url.path}")

    # Capture start time for latency measurement
    start_time = time.time()

    # Get or generate request ID
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
    trace_id_for_context = trace_id if trace_id else request_id
    trace = f"projects/{self.project_id}/traces/{trace_id_for_context}"
    request.state.trace = trace

    # Add session_id if available
    session_id = request.headers.get("X-Session-ID", "-")
    request.state.session_id = session_id

    request.state.start_time = start_time

    # Set the context variables for this request and store tokens
    context_tokens = set_context(
      request_id=request_id,
      trace=trace,
      session_id=session_id
    )

    # Debug context vars after setting
    #self.logger.debug(f"Context set: {debug_context_vars()}")

    try:
      # Process the request - this awaits and might lose context
      # But we've already set the state on the request object which helps
      response = await call_next(request)

      # Calculate request metrics
      request_latency = time.time() - start_time
      method = request.method
      path = request.url.path

      # Collect metrics if enabled
      if self.collect_metrics and self.request_latency and self.request_count:
        self.request_latency.labels(
          self.service_name, method, path
        ).observe(request_latency)

        self.request_count.labels(
          self.service_name, method, path, response.status_code
        ).inc()

      # Add request ID to response headers
      response.headers["X-Request-ID"] = request_id

      # Log request completion (debug level) and include ids
      # Re-assert the context to ensure proper logging
      with AsyncContextPreserver():
        # Restore the context for this request
        temp_tokens = set_context(
          request_id=request_id,
          trace=trace,
          session_id=session_id
        )

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

        # These tokens are temporary just for the log above
        reset_context(temp_tokens)

      return response

    except Exception as exc:
      # Handle and log exceptions
      error_type = type(exc).__name__

      if self.collect_metrics and self.error_count:
        self.error_count.labels(
          self.service_name, request.method, request.url.path, error_type
        ).inc()

      # Re-assert the context to ensure proper logging
      with AsyncContextPreserver():
        # Restore the context for this request
        temp_tokens = set_context(
          request_id=request_id,
          trace=trace,
          session_id=session_id
        )

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

        # These tokens are temporary just for the log above
        reset_context(temp_tokens)

      # Re-raise the original exception
      raise
    finally:
      # Debug context variables before reset
      #self.logger.debug(f"Request finishing: {debug_context_vars()}")

      # Reset context variables to previous values
      # IMPORTANT: Wait until the end of the request to reset
      reset_context(context_tokens)

      # Debug after reset
      #self.logger.debug(f"Context reset: {debug_context_vars()}")
