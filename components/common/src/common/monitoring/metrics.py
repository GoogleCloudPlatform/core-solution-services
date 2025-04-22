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
import inspect
import logging
from functools import wraps
from typing import Callable, Optional, Dict, Any, AsyncGenerator
from prometheus_client import Counter, Histogram, Gauge, Summary
from common.utils.logging_handler import Logger

__all__ = ["Counter",
           "Histogram",
           "Gauge",
           "Summary",
           "operation_tracker",
           "extract_user_id",
           "log_operation_result",
           "safe_extract_config_dict",
           "measure_latency",
           "track_streaming_response_size",
           "record_response_size",
           "record_user_activity"]

# Default logger
logger = Logger.get_logger("common.monitoring.metrics")


def filter_metric_labels(metric, labels, additional_labels=None):
  """Filter labels to only include those defined in the metric.
  
  Args:
      metric: The prometheus metric object
      labels: Dictionary of labels to filter
      additional_labels: Additional labels to include (e.g., status)
  
  Returns:
      Dictionary containing only the labels that are valid for this metric
  """
  # Get the label names defined for this metric
  metric_labelnames = getattr(metric, "_labelnames", [])

  # Combine with additional labels if provided
  if additional_labels:
    combined_labels = {**labels, **additional_labels}
  else:
    combined_labels = labels.copy() if labels else {}

  # Filter to include only valid labels
  filtered_labels = {
    k: v for k, v in combined_labels.items()
    if k in metric_labelnames
  }

  return filtered_labels


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


def _capitalize_first_letter(text: str) -> str:
  """Capitalize only the first letter of a string.
  
  Args:
      text: The text to capitalize
      
  Returns:
      Text with only the first letter capitalized
  """
  text = text.replace("_", " ")
  if not text:
    return text
  return text[0].upper() + text[1:]


def log_operation_result(
    log_instance: logging.Logger,
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

  operation_formatted = _capitalize_first_letter(operation_type)
  
  if status == "success":
    log_instance.info(
      f"{operation_formatted} successful",
      extra=extra
    )
  else:
    log_instance.error(
      f"{operation_formatted} failed",
      extra=extra
    )


def safe_extract_config_dict(config: Any) -> Dict[str, Any]:
  """Safely extract dictionary from config object
  
  Args:
      config: Config object (Pydantic model or similar)
      
  Returns:
      dict: Extracted configuration or empty dict on error
  """
  if not config:
    return {}

  try:
    if hasattr(config, "dict"):
      return config.dict()
    elif hasattr(config, "model_dump"):
      return config.model_dump()
    else:
      return dict(config)
  except (TypeError, AttributeError, ValueError, KeyError) as e:
    logger.error(
      f"Error extracting config dictionary: {type(e).__name__}: {e}"
    )
    return {}


def measure_latency(start_time: float, metric_name: str,
                     extra_data: Dict[str, Any] = None) -> float:
  """Calculate and log latency information
  
  Args:
      start_time: Start time from time.time()
      metric_name: Name of the operation for logging
      extra_data: Additional data to include in the log
      
  Returns:
      float: Latency in seconds
  """
  latency = time.time() - start_time

  if extra_data is None:
    extra_data = {}

  logger.info(
    f"{metric_name} latency",
    extra={
      "metric_type": f"Latency measured for {metric_name}",
      "duration_ms": round(latency * 1000, 2),
      **extra_data
    }
  )

  return latency


async def track_streaming_response_size(
    generator: AsyncGenerator,
    response_size_metric: Histogram,
    metric_type: str,
    extra_data: Dict[str, Any] = None
) -> AsyncGenerator:
  """Track size of streaming response
  
  Args:
      generator: Original async generator
      response_size_metric: Histogram metric to record size
      metric_type: Type of the response (e.g., "llm", "chat")
      extra_data: Additional data for logging
      
  Returns:
      An async generator that tracks size
  """
  if extra_data is None:
    extra_data = {}

  total_chars = 0
  try:
    logger.debug(
      "Starting streaming response tracking",
      extra={"metric_type": "streaming_debug", "response_type": metric_type}
    )

    async for chunk in generator:
      if isinstance(chunk, str):
        chunk_size = len(chunk)
        total_chars += chunk_size
      yield chunk

    logger.debug(
      f"Completed streaming with {total_chars} total characters",
      extra={"metric_type": "streaming_debug", "response_type": metric_type}
    )
  except Exception as e:
    logger.error(
      f"Error in streaming: {str(e)}",
      extra={"metric_type": "streaming_error", "response_type": metric_type}
    )
    raise
  finally:
    # Record size metrics
    logger.info(
      "Response size",
      extra={
        "metric_type": f"{metric_type}_response_size",
        "response_type": metric_type,
        "is_streaming": True,
        "response_size_chars": total_chars,
        **extra_data
      }
    )
    response_size_metric.labels(metric_type).observe(total_chars)


def record_response_size(
    result: Any,
    response_size_metric: Histogram,
    metric_type: str,
    extra_data: Dict[str, Any] = None
) -> int:
  """Record size for non-streaming responses
  
  Args:
      result: The response to measure
      response_size_metric: Histogram metric to record size
      metric_type: Type of the response (e.g., "llm", "chat")
      extra_data: Additional data for logging
      
  Returns:
      int: Size of the response
  """
  if extra_data is None:
    extra_data = {}

  response_size = 0

  if isinstance(result, str):
    response_size = len(result)
  elif isinstance(result, dict) and "content" in result:
    response_size = len(result["content"]) if isinstance(
      result["content"], str) else 0

  if response_size > 0:
    logger.info(
      "Response size",
      extra={
        "metric_type": f"{metric_type}_response_size",
        "response_type": metric_type,
        "is_streaming": False,
        "response_size_chars": response_size,
        **extra_data
      }
    )
    response_size_metric.labels(metric_type).observe(response_size)

  return response_size


def record_user_activity(
    user_id: str,
    activity_type: str,
    activity_counter: Counter
) -> None:
  """Record user activity for tracking active users
  
  Args:
      user_id: The user's ID (usually email)
      activity_type: Type of activity (e.g., 'chat', 'query', 'login')
      activity_counter: Counter metric to increment
  """
  if user_id and user_id != "unknown":
    activity_counter.labels(
      user_id=user_id,
      activity_type=activity_type
    ).inc()


def create_decorator_for_streaming_func(
    count_metric: Counter,
    latency_metric: Histogram,
    response_size_metric: Histogram = None,
    activity_counter: Counter = None,
    activity_type: str = None,
    metric_name: str = "operation",
    extract_labels_func: Callable = None
) -> Callable:
  """Create a decorator for functions that may return streaming results
  
  Args:
      count_metric: Counter metric for tracking operation counts
      latency_metric: Histogram metric for tracking operation latency
      response_size_metric: Optional histogram metric for response size
      activity_counter: Optional counter for user activity
      activity_type: Type of activity for user tracking
      metric_name: Name of the metric for logging
      extract_labels_func: Function to extract labels from kwargs
      
  Returns:
      Decorator function
  """

  def decorator(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
      # Extract user information
      user_data = kwargs.get("user_data")
      user_id = extract_user_id(user_data)

      # Extract metric labels if function provided
      labels = {}
      if extract_labels_func:
        try:
          labels = extract_labels_func(kwargs)
        except Exception as e:
          logger.error(f"Error extracting labels: {str(e)}")
          raise

      # Record user activity if counter provided
      if activity_counter and activity_type and user_id != "unknown":
        record_user_activity(user_id, activity_type, activity_counter)

      # Start timing
      start_time = time.time()

      try:
        # Call original function
        result = await func(*args, **kwargs)

        # Handle streaming responses if size metric provided
        if response_size_metric and (
          inspect.isasyncgen(result) or asyncio.iscoroutine(result)):
          # Wrap with size tracking generator
          original_result = result
          result = track_streaming_response_size(
            generator=original_result,
            response_size_metric=response_size_metric,
            metric_type=metric_name,
            extra_data=labels
          )
        elif response_size_metric:
          # Record size for non-streaming response
          record_response_size(
            result,
            response_size_metric,
            metric_name,
            labels
          )

        # Log success - FIXED: Filter labels to match metric definition
        filtered_success_labels = filter_metric_labels(
          count_metric,
          labels,
          {"status": "success"}
        )
        count_metric.labels(**filtered_success_labels).inc()

        log_operation_result(
          logger,
          metric_name,
          "success",
          labels
        )

        return result

      except Exception as e:
        # Log error - FIXED: Filter labels to match metric definition
        filtered_error_labels = filter_metric_labels(
          count_metric,
          labels,
          {"status": "error"}
        )
        count_metric.labels(**filtered_error_labels).inc()

        error_data = {**labels, "error_message": str(e)}
        log_operation_result(
          logger,
          metric_name,
          "error",
          error_data
        )
        raise

      finally:
        # Record latency - FIXED: Filter labels to match metric definition
        latency = measure_latency(
          start_time,
          metric_name,
          labels
        )
        filtered_latency_labels = filter_metric_labels(latency_metric, labels)
        latency_metric.labels(**filtered_latency_labels).observe(latency)

    return wrapper

  return decorator
