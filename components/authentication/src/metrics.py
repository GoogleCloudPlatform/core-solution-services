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

from common.monitoring.metrics import (
  Counter, Histogram, Gauge,
  operation_tracker
)
from common.utils.logging_handler import Logger

# Initialize logger
logger = Logger.get_logger("authentication_service.metrics")

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
  "concurrent_auth_operations",
  "Number of Concurrent Authentication Operations",
  ["operation"]
)

# Mapping of operation types to specific counters
OPERATION_COUNTERS = {
  "signup": USER_SIGNUP_COUNT,
  "signin": USER_SIGNIN_COUNT,
  "password_reset": PASSWORD_RESET_COUNT,
  "token_validation": TOKEN_VALIDATION_COUNT,
  "token_refresh": TOKEN_REFRESH_COUNT
}

def track_auth_operation(operation_type: str):
  """Decorator to track authentication operations.
  
  Uses the common operation_tracker but adds auth-specific metric tracking.
  
  Args:
      operation_type: Type of authentication operation
      
  Returns:
      Decorator function for the specified operation type
  """
  # Get specific counter for this operation type if it exists
  specific_counter = OPERATION_COUNTERS.get(operation_type)

  def decorator(func: Callable):
    # Create generic tracker using common utility
    tracked_func = operation_tracker(
      operation_type=operation_type,
      operation_counter=AUTH_OPERATION_COUNT,
      latency_histogram=AUTH_OPERATION_LATENCY,
      concurrent_gauge=CONCURRENT_OPERATIONS,
      custom_logger=logger
    )(func)

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
      try:
        # Call function with generic tracking
        result = await tracked_func(*args, **kwargs)

        # Increment specific counter if it exists
        if specific_counter:
          status = "success"
          if isinstance(result, dict) and not result.get("success", True):
            status = "error"
          specific_counter.labels(status=status).inc()

        return result
      except Exception:
        # Increment specific counter for errors
        if specific_counter:
          specific_counter.labels(status="error").inc()

        # Re-raise the exception
        raise

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
      try:
        # Call function with generic tracking
        result = tracked_func(*args, **kwargs)

        # Increment specific counter if it exists
        if specific_counter:
          status = "success"
          if isinstance(result, dict) and not result.get("success", True):
            status = "error"
          specific_counter.labels(status=status).inc()

        return result
      except Exception:
        # Increment specific counter for errors
        if specific_counter:
          specific_counter.labels(status="error").inc()

        # Re-raise the exception
        raise

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    else:
      return sync_wrapper

  return decorator

# Convenience decorators for specific auth operations
track_signup = track_auth_operation("signup")
track_signin = track_auth_operation("signin")
track_password_reset = track_auth_operation("password_reset")
track_token_validation = track_auth_operation("token_validation")
track_token_refresh = track_auth_operation("token_refresh")
