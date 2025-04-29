"""Common monitoring middleware components for request tracking and metrics."""

import time
import uuid
import logging
import re
import contextvars
from fastapi import Request, Response
from fastapi.routing import APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Optional, Dict
from prometheus_client import (
  Counter,
  Histogram,
  generate_latest,
  CONTENT_TYPE_LATEST
)

# Try importing context variables from context_vars first
try:
  from common.utils.context_vars import (
    request_id_var, trace_var, session_id_var,
    get_context, set_context, reset_context, AsyncContextPreserver
  )
  print("*** STARTUP: Successfully imported from context_vars ***")
except ImportError:
  # Fall back to importing from logging_handler if context_vars not available
  try:
    from common.utils.logging_handler import (
      request_id_var, trace_var, session_id_var
    )
    print("*** STARTUP: Successfully imported from logging_handler ***")

    cloud_trace_context_var = contextvars.ContextVar("cloud_trace_context", default="-")

    # Define missing functions if not available from logging_handler
    def get_context() -> Dict[str, str]:
      """Get all context variables as a dictionary."""
      return {
        "request_id": request_id_var.get(),
        "trace": trace_var.get(),
        "session_id": session_id_var.get(),
        "cloud_trace_context": cloud_trace_context_var.get()
      }

    def set_context(
      request_id: Optional[str] = None,
      trace: Optional[str] = None,
      session_id: Optional[str] = None,
      cloud_trace_context: Optional[str] = None
    ) -> list:
      """Set context variables and return tokens for resetting."""
      tokens = []

      if request_id is not None:
        token = request_id_var.set(request_id)
        tokens.append((request_id_var, token))

      if trace is not None:
        token = trace_var.set(trace)
        tokens.append((trace_var, token))

      if session_id is not None:
        token = session_id_var.set(session_id)
        tokens.append((session_id_var, token))
        
      if cloud_trace_context is not None:
        token = cloud_trace_context_var.set(cloud_trace_context)
        tokens.append((cloud_trace_context_var, token))

      return tokens

    def reset_context(tokens: list) -> None:
      """Reset context variables using the tokens from set_context."""
      for var, token in tokens:
        var.reset(token)

    class AsyncContextPreserver:
      """Context manager to preserve context vars across async boundaries."""

      def __init__(self):
        self.tokens = None
        self.preserved_context = None

      def __enter__(self):
        # Save current context
        self.preserved_context = get_context()
        return self.preserved_context

      def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore context
        if self.preserved_context:
          _ = set_context(
            request_id=self.preserved_context.get("request_id"),
            trace=self.preserved_context.get("trace"),
            session_id=self.preserved_context.get("session_id"),
            cloud_trace_context=self.preserved_context.get("cloud_trace_context")
          )
  except ImportError as e:
    # Define context vars locally if all imports fail
    print(f"*** STARTUP: Import from logging_handler failed: {e} ***")
    print("*** STARTUP: Defining local context vars ***")

    request_id_var = contextvars.ContextVar("request_id", default="-")
    trace_var = contextvars.ContextVar("trace", default="-")
    session_id_var = contextvars.ContextVar("session_id", default="-")
    cloud_trace_context_var = contextvars.ContextVar("cloud_trace_context", default="-")

    def get_context() -> Dict[str, str]:
      """Get all context variables as a dictionary."""
      return {
        "request_id": request_id_var.get(),
        "trace": trace_var.get(),
        "session_id": session_id_var.get(),
        "cloud_trace_context": cloud_trace_context_var.get()
      }

    def set_context(
      request_id: Optional[str] = None,
      trace: Optional[str] = None,
      session_id: Optional[str] = None,
      cloud_trace_context: Optional[str] = None
    ) -> list:
      """Set context variables and return tokens for resetting."""
      tokens = []

      if request_id is not None:
        token = request_id_var.set(request_id)
        tokens.append((request_id_var, token))

      if trace is not None:
        token = trace_var.set(trace)
        tokens.append((trace_var, token))

      if session_id is not None:
        token = session_id_var.set(session_id)
        tokens.append((session_id_var, token))
        
      if cloud_trace_context is not None:
        token = cloud_trace_context_var.set(cloud_trace_context)
        tokens.append((cloud_trace_context_var, token))

      return tokens

    def reset_context(tokens: list) -> None:
      """Reset context variables using the tokens from set_context."""
      for var, token in tokens:
        var.reset(token)

    class AsyncContextPreserver:
      """Context manager to preserve context vars across async boundaries."""

      def __init__(self):
        self.tokens = None
        self.preserved_context = None

      def __enter__(self):
        # Save current context
        self.preserved_context = get_context()
        return self.preserved_context

      def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore context
        if self.preserved_context:
          _ = set_context(
            request_id=self.preserved_context.get("request_id"),
            trace=self.preserved_context.get("trace"),
            session_id=self.preserved_context.get("session_id"),
            cloud_trace_context=self.preserved_context.get("cloud_trace_context")
          )

try:
  from common.config import PROJECT_ID
except (ImportError, AttributeError):
  PROJECT_ID = "unknown-project"

try:
  from common.utils.logging_handler import Logger
  print("*** STARTUP: middleware.py imported Logger from logging_handler ***")
except ImportError as e:
  print(f"*** STARTUP: Import of Logger from logging_handler failed: {e} ***")
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
    """Process request, adds tracking IDs, and collects metrics.
    
    This method carefully manages context propagation across await boundaries.
    """
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

    request_id = request.headers.get("X-Request-ID")
    cloud_trace_context = request.headers.get("X-Cloud-Trace-Context")
    
    # Store the raw cloud trace context
    request.state.cloud_trace_context = cloud_trace_context

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
      session_id=session_id,
      cloud_trace_context=cloud_trace_context
    )

    try:
      # Process the request - this awaits and might lose context
      # But we've already set the state on the request object which helps
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
      if request_id:
        response.headers["X-Request-ID"] = request_id
      
      # Add cloud trace context to response headers if present
      if cloud_trace_context:
        response.headers["X-Cloud-Trace-Context"] = cloud_trace_context

      # Log request completion (debug level) and include ids
      # Re-assert the context to ensure proper logging
      with AsyncContextPreserver():
        # Restore the context for this request
        temp_tokens = set_context(
          request_id=request_id,
          trace=trace,
          session_id=session_id,
          cloud_trace_context=cloud_trace_context
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

      if self.collect_metrics:
        self.error_count.labels(
          self.service_name, request.method, request.url.path, error_type
        ).inc()

      # Re-assert the context to ensure proper logging
      with AsyncContextPreserver():
        # Restore the context for this request
        temp_tokens = set_context(
          request_id=request_id,
          trace=trace,
          session_id=session_id,
          cloud_trace_context=cloud_trace_context
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
      # Reset context variables to previous values
      # IMPORTANT: Wait until the end of the request to reset
      reset_context(context_tokens)

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

def get_request_context(args) -> Dict[str, str]:
  """Extract request_id, trace and session_id from request if available.
  
  Args:
    args: Arguments passed to the decorated function
      
  Returns:
    Dict containing request_id, trace, session_id extracted from arguments
  """
  # First check context vars (for use outside of request handlers)
  context = get_context()
  request_id = context["request_id"]
  trace = context["trace"]
  session_id = context["session_id"]
  cloud_trace_context = context.get("cloud_trace_context", "-")

  # Then try to extract from request if available
  for arg in args:
    if hasattr(arg, "state"):
      request_id = getattr(arg.state, "request_id", request_id)
      trace = getattr(arg.state, "trace", trace)
      session_id = getattr(arg.state, "session_id", session_id)
      cloud_trace_context = getattr(arg.state, "cloud_trace_context", cloud_trace_context)
      break

  return {
    "request_id": request_id,
    "trace": trace,
    "session_id": session_id,
    "cloud_trace_context": cloud_trace_context
  }
