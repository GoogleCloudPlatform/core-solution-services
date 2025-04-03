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
from fastapi import Request, Response
from fastapi.routing import APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Optional
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

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

  def __init__(
      self, 
      app,
      project_id: str = None,
      service_name: str = "service",
      collect_metrics: bool = False,
      request_count_metric: Optional[Counter] = None,
      request_latency_metric: Optional[Histogram] = None,
      error_count_metric: Optional[Counter] = None,
      log_factory_reset: bool = True
  ):
    """Initialize the middleware with configuration options.
    
    Args:
        app: The FastAPI application
        project_id: Google Cloud project ID for trace context (if None, attempts to get from common.config)
        service_name: Name of the service (used for metrics)
        collect_metrics: Whether to collect Prometheus metrics
        request_count_metric: Optional custom Counter for request counts
        request_latency_metric: Optional custom Histogram for request latency
        error_count_metric: Optional custom Counter for error counts
        log_factory_reset: Whether to reset the log factory after request processing
    """
    super().__init__(app)
    
    # If project_id not provided, try to get from common.config
    if project_id is None:
      try:
        from common.config import PROJECT_ID
        project_id = PROJECT_ID
      except (ImportError, AttributeError):
        project_id = "unknown-project"
    
    self.project_id = project_id
    self.service_name = service_name
    self.collect_metrics = collect_metrics
    self.request_count = request_count_metric or REQUEST_COUNT
    self.request_latency = request_latency_metric or REQUEST_LATENCY
    self.error_count = error_count_metric or ERROR_COUNT
    self.log_factory_reset = log_factory_reset
    self.logger = self._get_logger()
    
  def _get_logger(self):
    """Get the logger for the middleware.
    
    Override this method if you want to use a custom logger.
    """
    try:
      from common.utils.logging_handler import Logger
      return Logger.get_logger(__file__)
    except ImportError:
      return logging.getLogger(__name__)

  async def dispatch(self, request: Request, call_next):
    # Capture start time for latency measurement
    start_time = time.time()
    
    # Get or generate request ID
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
      request_id = str(uuid.uuid4())
    
    # Store request context in request state
    request.state.request_id = request_id
    request.state.start_time = start_time
    trace = f"projects/{self.project_id}/traces/{request_id}"
    request.state.trace = trace

    # Create a custom log record factory to inject request context
    original_factory = logging.getLogRecordFactory()

    def custom_log_record_factory(*args, **kwargs):
      record = original_factory(*args, **kwargs)
      record.request_id = request.state.request_id
      record.trace = request.state.trace
      return record

    logging.setLogRecordFactory(custom_log_record_factory)

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
      
      # Log request completion (debug level)
      self.logger.debug(
        "Request processed",
        extra={
          "metric_type": "request",
          "method": method,
          "path": path,
          "status_code": response.status_code,
          "duration_ms": round(request_latency * 1000, 2),
          "request_id": request_id,
          "trace": trace
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
          "error_message": str(e),
          "request_id": request_id,
          "trace": trace
        }
      )
      
      raise
    finally:
      # Reset log factory if configured to do so
      if self.log_factory_reset:
        logging.setLogRecordFactory(original_factory)

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
    
    # Extract request_id and trace from request state
    request_id = getattr(request.state, "request_id", "-")
    trace = getattr(request.state, "trace", "-")

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
  """Extract request_id and trace from request if available.
  
  Args:
      args: Arguments passed to the decorated function
      
  Returns:
      tuple: (request_id, trace) extracted from arguments or defaults
  """
  request_id = "-"
  trace = "-"

  for arg in args:
    if hasattr(arg, "state"):
      request_id = getattr(arg.state, "request_id", "-")
      trace = getattr(arg.state, "trace", "-")
      break

  return request_id, trace
