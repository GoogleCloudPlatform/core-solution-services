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

"""Authentication service-specific metrics and tracking decorators"""

import asyncio
from functools import wraps
from typing import Callable
from common.monitoring.metrics import Counter, Histogram, Gauge
from common.utils.logging_handler import Logger
from common.monitoring.metrics import operation_tracker

# Initialize logger
logger = Logger.get_logger(__file__)

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

def track_auth_operation(operation_type: str):
  """Decorator to track authentication operations.
  
  Uses the common operation_tracker but adds auth-specific metric tracking.
  
  Args:
      operation_type: Type of authentication operation
      
  Returns:
      Decorator function for the specified operation type
  """
  # Create generic tracker using common utility
  generic_tracker = operation_tracker(
    operation_type=operation_type,
    operation_counter=AUTH_OPERATION_COUNT,
    latency_histogram=AUTH_OPERATION_LATENCY,
    concurrent_gauge=CONCURRENT_OPERATIONS,
    custom_logger=logger
  )

  def decorator(func: Callable):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
      # Call function with generic tracking
      try:
        result = await generic_tracker(func)(*args, **kwargs)

        # Determine success or failure based on result
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

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

        return result
      except Exception:
        # Increment specific counter for errors
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

        # Re-raise the exception without capturing it
        raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
      # Call function with generic tracking
      try:
        result = generic_tracker(func)(*args, **kwargs)

        # Determine success or failure based on result
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

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

        return result
      except Exception:
        # Increment specific counter for errors
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

        # Re-raise the exception without capturing it
        raise

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    else:
      return sync_wrapper

  return decorator

# Convenience decorators for specific auth operations
def track_signup(func):
  """Track signup operations."""
  return track_auth_operation("signup")(func)

def track_signin(func):
  """Track signin operations."""
  return track_auth_operation("signin")(func)

def track_password_reset(func):
  """Track password reset operations."""
  return track_auth_operation("password_reset")(func)

def track_token_validation(func):
  """Track token validation operations."""
  return track_auth_operation("token_validation")(func)

def track_token_refresh(func):
  """Track token refresh operations."""
  return track_auth_operation("token_refresh")(func)
