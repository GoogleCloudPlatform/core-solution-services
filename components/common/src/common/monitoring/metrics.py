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

"""Common metrics utilities and shared functions for all services."""

import time
import asyncio
import logging
from functools import wraps
from typing import Callable, Optional, Dict, Any
from prometheus_client import Counter, Histogram, Gauge, Summary
from common.utils.logging_handler import Logger

__all__ = ['Counter', 'Histogram', 'Gauge', 'Summary', 'operation_tracker', 'extract_user_id', 'log_operation_result']

# Default logger
logger = Logger.get_logger(__file__)

def operation_tracker(
    operation_type: str,
    operation_counter: Counter,
    latency_histogram: Histogram,
    concurrent_gauge: Optional[Gauge] = None,
    custom_logger: Optional[logging.Logger] = None
):
  """Generic decorator factory for tracking operations with Prometheus metrics.
  
  Args:
      operation_type: Type/name of the operation being tracked
      operation_counter: Counter metric for tracking operation counts
      latency_histogram: Histogram metric for tracking operation latency
      concurrent_gauge: Optional gauge for tracking concurrent operations
      custom_logger: Optional logger instance for additional logging
      
  Returns:
      callable: Decorator function
  """
  # Use provided logger or default
  log = custom_logger or logger

  def decorator(func: Callable):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
      # Track concurrent operations if gauge provided
      if concurrent_gauge:
        concurrent_gauge.labels(operation=operation_type).inc()

      # Track latency
      start_time = time.time()
      try:
        # Execute the function
        result = await func(*args, **kwargs)

        # Determine success/failure status
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

        # Record operation count
        operation_counter.labels(
          operation=operation_type,
          status=status
        ).inc()

        # Log if logger provided
        log.info(
          f"{operation_type.replace('_', ' ').title()} operation successful",
          extra={
            "metric_type": "operation",
            "operation": operation_type,
            "status": status
          }
        )

        return result
      except Exception as e:
        # Record error
        operation_counter.labels(
          operation=operation_type,
          status="error"
        ).inc()

        # Log error if logger provided
        log.error(
          f"{operation_type.replace('_', ' ').title()} operation failed",
          extra={
            "metric_type": "operation",
            "operation": operation_type,
            "status": "error",
            "error_message": str(e)
          }
        )

        raise
      finally:
        # Record latency
        latency = time.time() - start_time
        latency_histogram.labels(operation=operation_type).observe(latency)

        # Log latency if logger provided
        log.info(
          f"{operation_type.replace('_', ' ').title()} operation latency",
          extra={
            "metric_type": "operation_latency",
            "operation": operation_type,
            "duration_ms": round(latency * 1000, 2)
          }
        )

        # Decrement concurrent operations counter if provided
        if concurrent_gauge:
          concurrent_gauge.labels(operation=operation_type).dec()

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
      # Track concurrent operations if gauge provided
      if concurrent_gauge:
        concurrent_gauge.labels(operation=operation_type).inc()

      # Track latency
      start_time = time.time()
      try:
        # Execute the function
        result = func(*args, **kwargs)

        # Determine success/failure status
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

        # Record operation count
        operation_counter.labels(
          operation=operation_type,
          status=status
        ).inc()

        # Log if logger provided
        log.info(
          f"{operation_type.replace('_', ' ').title()} operation successful",
          extra={
            "metric_type": "operation",
            "operation": operation_type,
            "status": status
          }
        )

        return result
      except Exception as e:
        # Record error
        operation_counter.labels(
          operation=operation_type,
          status="error"
        ).inc()

        # Log error if logger provided
        log.error(
          f"{operation_type.replace('_', ' ').title()} operation failed",
          extra={
            "metric_type": "operation",
            "operation": operation_type,
            "status": "error",
            "error_message": str(e)
          }
        )

        raise
      finally:
        # Record latency
        latency = time.time() - start_time
        latency_histogram.labels(operation=operation_type).observe(latency)

        # Log latency if logger provided
        log.info(
          f"{operation_type.replace('_', ' ').title()} operation latency",
          extra={
            "metric_type": "operation_latency",
            "operation": operation_type,
            "duration_ms": round(latency * 1000, 2)
          }
        )

        # Decrement concurrent operations counter if provided
        if concurrent_gauge:
          concurrent_gauge.labels(operation=operation_type).dec()

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    else:
      return sync_wrapper

  return decorator


def extract_user_id(user_data: Optional[Dict[str, Any]]) -> str:
  """Extract user ID from user data dict if available.
  
  Args:
      user_data: Dictionary potentially containing user information
      
  Returns:
      str: User ID (usually email) or "unknown" if not found
  """
  if user_data and isinstance(user_data, dict):
    return user_data.get("email", "unknown")
  return "unknown"


def log_operation_result(
    logger: logging.Logger,
    operation_type: str,
    status: str,
    additional_data: Optional[Dict[str, Any]] = None
):
  """Log operation result with consistent format.
  
  Args:
      logger: Logger instance to use
      operation_type: Type of operation being performed
      status: Status of operation ('success' or 'error')
      additional_data: Additional data to include in log
  """
  extra = {
    "metric_type": f"{operation_type}",
    "operation": operation_type,
    "status": status
  }

  if additional_data:
    extra.update(additional_data)

  if status == "success":
    logger.info(f"{operation_type.replace('_', ' ').title()} successful", extra=extra)
  else:
    logger.error(f"{operation_type.replace('_', ' ').title()} failed", extra=extra)
