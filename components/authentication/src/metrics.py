# Copyright 2025 Google LLC
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

"""Prometheus metrics and instrumentation for the Authentication Service"""

import time
import asyncio
import logging
import uuid
from typing import Callable, Dict, Any
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.routing import APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from common.config import PROJECT_ID

from common.utils.logging_handler import Logger
logger = Logger.get_logger(__file__)

# Fast level request Metrics
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

# Authentication-specific Metrics
AUTH_OPERATION_COUNT = Counter(
  "auth_operation_count", "Authentication Operations Count",
  ["operation", "status"]
)

AUTH_OPERATION_LATENCY = Histogram(
  "auth_operation_latency_seconds", "Authentication Operation Latency",
  ["operation"]
)

# User Metrics
USER_SIGNUP_COUNT = Counter(
  "user_signup_count", "User Signup Count",
  ["status"]
)

USER_SIGNIN_COUNT = Counter(
  "user_signin_count", "User Signin Count",
  ["status"]
)

PASSWORD_RESET_COUNT = Counter(
  "password_reset_count", "Password Reset Count",
  ["status"]
)

TOKEN_VALIDATION_COUNT = Counter(
  "token_validation_count", "Token Validation Count",
  ["status"]
)

TOKEN_REFRESH_COUNT = Counter(
  "token_refresh_count", "Token Refresh Count",
  ["status"]
)

# Active Users Gauge
ACTIVE_USERS = Gauge(
  "active_users", "Number of Active Users",
  ["time_window"]
)

# For tracking concurrent operations
CONCURRENT_OPERATIONS = Gauge(
  "concurrent_auth_operations", "Number of Concurrent Authentication Operations",
  ["operation"]
)

class RequestTrackingMiddleware(BaseHTTPMiddleware):
  """Middleware to inject request_id and trace into logs and track requests."""

  async def dispatch(self, request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
      request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.start_time = time.time()
    trace = f"projects/{PROJECT_ID}/traces/{request_id}"
    request.state.trace = trace

    # Create a custom log record factory to inject request_id and trace
    original_factory = logging.getLogRecordFactory()

    def custom_log_record_factory(*args, **kwargs):
      record = original_factory(*args, **kwargs)
      record.request_id = request.state.request_id
      record.trace = request.state.trace
      return record

    logging.setLogRecordFactory(custom_log_record_factory)

    try:
      response = await call_next(request)
      request_latency = time.time() - request.state.start_time

      method = request.method
      path = request.url.path

      REQUEST_LATENCY.labels(
        "auth_service", method, path
      ).observe(request_latency)

      REQUEST_COUNT.labels(
        "auth_service", method, path, response.status_code
      ).inc()

      logger.debug(
        "Request processed",
        extra={
          "metric_type": "request",
          "method": method,
          "path": path,
          "status_code": response.status_code,
          "duration_ms": round(request_latency * 1000, 2)
        }
      )

      response.headers["X-Request-ID"] = request_id
      return response
    except Exception as e:
      error_type = type(e).__name__
      ERROR_COUNT.labels(
        "auth_service", request.method, request.url.path, error_type
      ).inc()

      logger.error(
        "Request error",
        extra={
          "metric_type": "request_error",
          "method": request.method,
          "path": request.url.path,
          "error_type": error_type,
          "error_message": str(e)
        }
      )

      # Restore original factory
      logging.setLogRecordFactory(original_factory)
      raise

class PrometheusMiddleware(BaseHTTPMiddleware):
  """Middleware to collect Prometheus metrics for all requests."""
  async def dispatch(self, request: Request, call_next):
    start_time = time.time()

    method = request.method
    path = request.url.path

    try:
      response = await call_next(request)
      request_latency = time.time() - start_time

      REQUEST_LATENCY.labels(
        "auth_service", method, path
      ).observe(request_latency)

      REQUEST_COUNT.labels(
        "auth_service", method, path, response.status_code
      ).inc()

      return response
    except Exception as e:
      error_type = type(e).__name__
      ERROR_COUNT.labels(
        "auth_service", method, path, error_type
      ).inc()
      raise

# prometheus needs its own router
def create_metrics_router() -> APIRouter:
  """Creates a router with the /metrics endpoint"""
  metrics_router = APIRouter(tags=["Metrics"])

  @metrics_router.get("/metrics")
  async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

  return metrics_router

def _get_request_context(args) -> tuple:
  """Extract request_id and trace from request if available"""
  request_id = "-"
  trace = "-"

  for arg in args:
    if hasattr(arg, "state"):
      request_id = getattr(arg.state, "request_id", "-")
      trace = getattr(arg.state, "trace", "-")
      break

  return request_id, trace

def track_auth_operation(operation_type: str):
  """Decorator to track authentication operations"""
  def decorator(func: Callable):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
      request_id, trace = _get_request_context(args)

      # Increment concurrent operations counter
      CONCURRENT_OPERATIONS.labels(operation=operation_type).inc()

      start_time = time.time()
      try:
        result = await func(*args, **kwargs)

        # Determine success or failure based on result
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

        AUTH_OPERATION_COUNT.labels(
          operation=operation_type, 
          status=status
        ).inc()

        # Increment specific counter based on operation type
        if operation_type == "signup":
          USER_SIGNUP_COUNT.labels(status=status).inc()
        elif operation_type == "signin":
          USER_SIGNIN_COUNT.labels(status=status).inc()
        elif operation_type == "password_reset":
          PASSWORD_RESET_COUNT.labels(status=status).inc()
        elif operation_type == "token_validation":
          TOKEN_VALIDATION_COUNT.labels(status=status).inc()
        elif operation_type == "token_refresh":
          TOKEN_REFRESH_COUNT.labels(status=status).inc()

        logger.info(
          f"{operation_type.replace('_', ' ').title()} operation successful",
          extra={
            "metric_type": "auth_operation",
            "operation": operation_type,
            "status": status,
            "request_id": request_id
          }
        )

        return result
      except Exception as e:
        AUTH_OPERATION_COUNT.labels(
          operation=operation_type, 
          status="error"
        ).inc()

        # Increment specific counter based on operation type
        if operation_type == "signup":
          USER_SIGNUP_COUNT.labels(status="error").inc()
        elif operation_type == "signin":
          USER_SIGNIN_COUNT.labels(status="error").inc()
        elif operation_type == "password_reset":
          PASSWORD_RESET_COUNT.labels(status="error").inc()
        elif operation_type == "token_validation":
          TOKEN_VALIDATION_COUNT.labels(status="error").inc()
        elif operation_type == "token_refresh":
          TOKEN_REFRESH_COUNT.labels(status="error").inc()

        logger.error(
          f"{operation_type.replace('_', ' ').title()} operation failed",
          extra={
            "metric_type": "auth_operation",
            "operation": operation_type,
            "status": "error",
            "error_message": str(e),
            "request_id": request_id
          }
        )
        raise
      finally:
        latency = time.time() - start_time
        AUTH_OPERATION_LATENCY.labels(operation=operation_type).observe(latency)

        logger.info(
          f"{operation_type.replace('_', ' ').title()} operation latency",
          extra={
            "metric_type": "auth_operation_latency",
            "operation": operation_type,
            "duration_ms": round(latency * 1000, 2),
            "request_id": request_id
          }
        )

        # Decrement concurrent operations counter
        CONCURRENT_OPERATIONS.labels(operation=operation_type).dec()

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
      request_id, trace = _get_request_context(args)

      # Increment concurrent operations counter
      CONCURRENT_OPERATIONS.labels(operation=operation_type).inc()

      start_time = time.time()
      try:
        result = func(*args, **kwargs)

        # Determine success or failure based on result
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

        AUTH_OPERATION_COUNT.labels(
          operation=operation_type, 
          status=status
        ).inc()

        # Increment specific counter based on operation type
        if operation_type == "signup":
          USER_SIGNUP_COUNT.labels(status=status).inc()
        elif operation_type == "signin":
          USER_SIGNIN_COUNT.labels(status=status).inc()
        elif operation_type == "password_reset":
          PASSWORD_RESET_COUNT.labels(status=status).inc()
        elif operation_type == "token_validation":
          TOKEN_VALIDATION_COUNT.labels(status=status).inc()
        elif operation_type == "token_refresh":
          TOKEN_REFRESH_COUNT.labels(status=status).inc()

        logger.info(
          f"{operation_type.replace('_', ' ').title()} operation successful",
          extra={
            "metric_type": "auth_operation",
            "operation": operation_type,
            "status": status,
            "request_id": request_id
          }
        )

        return result
      except Exception as e:
        AUTH_OPERATION_COUNT.labels(
          operation=operation_type, 
          status="error"
        ).inc()

        # Increment specific counter based on operation type
        if operation_type == "signup":
          USER_SIGNUP_COUNT.labels(status="error").inc()
        elif operation_type == "signin":
          USER_SIGNIN_COUNT.labels(status="error").inc()
        elif operation_type == "password_reset":
          PASSWORD_RESET_COUNT.labels(status="error").inc()
        elif operation_type == "token_validation":
          TOKEN_VALIDATION_COUNT.labels(status="error").inc()
        elif operation_type == "token_refresh":
          TOKEN_REFRESH_COUNT.labels(status="error").inc()

        logger.error(
          f"{operation_type.replace('_', ' ').title()} operation failed",
          extra={
            "metric_type": "auth_operation",
            "operation": operation_type,
            "status": "error",
            "error_message": str(e),
            "request_id": request_id
          }
        )
        raise
      finally:
        latency = time.time() - start_time
        AUTH_OPERATION_LATENCY.labels(operation=operation_type).observe(latency)

        logger.info(
          f"{operation_type.replace('_', ' ').title()} operation latency",
          extra={
            "metric_type": "auth_operation_latency",
            "operation": operation_type,
            "duration_ms": round(latency * 1000, 2),
            "request_id": request_id
          }
        )

        # Decrement concurrent operations counter
        CONCURRENT_OPERATIONS.labels(operation=operation_type).dec()

    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    else:
      return sync_wrapper

  return decorator

# Decorators for auth operations
def track_signup(func):
  return track_auth_operation("signup")(func)

def track_signin(func):
  return track_auth_operation("signin")(func)

def track_password_reset(func):
  return track_auth_operation("password_reset")(func)

def track_token_validation(func):
  return track_auth_operation("token_validation")(func)

def track_token_refresh(func):
  return track_auth_operation("token_refresh")(func)
