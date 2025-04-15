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

"""User management service-specific metrics and tracking decorators"""

import time
import asyncio
from functools import wraps
from typing import Callable, Dict, Any

from common.models import User
from common.utils.logging_handler import Logger
from common.monitoring.metrics import (
  Counter, Histogram, Gauge,
  log_operation_result, measure_latency
)

# Initialize logger
logger = Logger.get_logger("user_management.metrics")

# User Management Operation Metrics
USER_OPERATION_COUNT = Counter(
  "user_operation_count", "User Operation Count",
  ["operation", "status"]
)

USER_OPERATION_LATENCY = Histogram(
  "user_operation_latency_seconds", "User Operation Latency",
  ["operation"]
)

# User CRUD Metrics
USER_CREATE_COUNT = Counter(
  "user_create_count", "User Creation Count",
  ["status"]
)

USER_UPDATE_COUNT = Counter(
  "user_update_count", "User Update Count",
  ["status"]
)

USER_DELETE_COUNT = Counter(
  "user_delete_count", "User Deletion Count",
  ["status"]
)

USER_GET_COUNT = Counter(
  "user_get_count", "User Retrieval Count",
  ["status"]
)

# User Group Metrics
USER_GROUP_OPERATION_COUNT = Counter(
  "user_group_operation_count", "User Group Operation Count",
  ["operation", "status"]
)

# User Status Metrics
USER_STATUS_UPDATE_COUNT = Counter(
  "user_status_update_count", "User Status Update Count",
  ["status_from", "status_to", "result"]
)

# Import Metrics
USER_IMPORT_COUNT = Counter(
  "user_import_count", "User Import Count",
  ["method", "status"]
)

USER_IMPORT_BATCH_SIZE = Histogram(
  "user_import_batch_size", "Number of Users in Import Batch",
  buckets=[1, 5, 10, 50, 100, 500, 1000]
)

# Active Users Metrics
ACTIVE_USERS_COUNT = Gauge(
  "active_users_count", "Number of Active Users",
  ["user_type"]
)

# Concurrent Operations
CONCURRENT_OPERATIONS = Gauge(
  "concurrent_user_operations", "Number of Concurrent User Operations",
  ["operation"]
)

# Mapping of operation types to specific counters
OPERATION_COUNTERS = {
  "create_user": USER_CREATE_COUNT,
  "update_user": USER_UPDATE_COUNT,
  "delete_user": USER_DELETE_COUNT,
  "get_user": USER_GET_COUNT
}

def extract_user_operation_labels(kwargs: Dict[str, Any]) -> Dict[str, str]:
  """Extract operation labels from kwargs
  
  Args:
      kwargs: Function keyword arguments
      
  Returns:
      Dict with operation labels
  """
  _ = kwargs
  # The label map will be used directly by the metric counters
  # Could add more logic here to extract additional labels if needed
  return {}

def track_user_operation(operation_type: str):
  """Decorator to track user management operations.
  
  Args:
      operation_type: Type of user operation
      
  Returns:
      Decorator function for the specified operation type
  """
  specific_counter = OPERATION_COUNTERS.get(operation_type)
  user_group_op = operation_type.startswith("user_group_")

  def decorator(func: Callable):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
      # Track concurrent operations
      CONCURRENT_OPERATIONS.labels(operation=operation_type).inc()

      # Start timing
      start_time = time.time()

      try:
        # Execute function
        result = await func(*args, **kwargs)

        # Determine success/failure status
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

        # Record operation metrics
        USER_OPERATION_COUNT.labels(
          operation=operation_type,
          status=status
        ).inc()

        # Record specific operation metrics based on operation type
        if specific_counter:
          specific_counter.labels(status=status).inc()
        elif user_group_op:
          USER_GROUP_OPERATION_COUNT.labels(
            operation=operation_type.replace("user_group_", ""),
            status=status
          ).inc()

        # Log success
        log_operation_result(
          logger,
          operation_type,
          "success",
          {"result": "success"}
        )

        return result
      except Exception as error:
        # Record error metrics
        USER_OPERATION_COUNT.labels(
          operation=operation_type,
          status="error"
        ).inc()

        # Record specific operation error metrics
        if specific_counter:
          specific_counter.labels(status="error").inc()
        elif user_group_op:
          USER_GROUP_OPERATION_COUNT.labels(
            operation=operation_type.replace("user_group_", ""),
            status="error"
          ).inc()

        # Log error
        log_operation_result(
          logger,
          operation_type,
          "error",
          {"error_message": str(error)}
        )

        raise
      finally:
        # Record latency
        latency = measure_latency(
          start_time,
          operation_type,
          {"operation": operation_type}
        )
        USER_OPERATION_LATENCY.labels(operation=operation_type).observe(latency)

        # Decrement concurrent operations
        CONCURRENT_OPERATIONS.labels(operation=operation_type).dec()

    @wraps(func)
    def sync_wrapper(*args, **kwargs):
      # Track concurrent operations
      CONCURRENT_OPERATIONS.labels(operation=operation_type).inc()

      # Start timing
      start_time = time.time()

      try:
        # Execute function
        result = func(*args, **kwargs)

        # Determine success/failure status
        status = "success"
        if isinstance(result, dict) and not result.get("success", True):
          status = "error"

        # Record operation metrics
        USER_OPERATION_COUNT.labels(
          operation=operation_type,
          status=status
        ).inc()

        # Record specific operation metrics based on operation type
        if specific_counter:
          specific_counter.labels(status=status).inc()
        elif user_group_op:
          USER_GROUP_OPERATION_COUNT.labels(
            operation=operation_type.replace("user_group_", ""),
            status=status
          ).inc()

        # Log success
        log_operation_result(
          logger,
          operation_type,
          "success",
          {"result": "success"}
        )

        return result
      except Exception as error:
        # Record error metrics
        USER_OPERATION_COUNT.labels(
          operation=operation_type,
          status="error"
        ).inc()

        # Record specific operation error metrics
        if specific_counter:
          specific_counter.labels(status="error").inc()
        elif user_group_op:
          USER_GROUP_OPERATION_COUNT.labels(
            operation=operation_type.replace("user_group_", ""),
            status="error"
          ).inc()

        # Log error
        log_operation_result(
          logger,
          operation_type,
          "error",
          {"error_message": str(error)}
        )

        raise
      finally:
        # Record latency
        latency = measure_latency(
          start_time,
          operation_type,
          {"operation": operation_type}
        )
        USER_OPERATION_LATENCY.labels(operation=operation_type).observe(latency)

        # Decrement concurrent operations
        CONCURRENT_OPERATIONS.labels(operation=operation_type).dec()

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    else:
      return sync_wrapper

  return decorator

def extract_user_status_info(args, kwargs) -> Dict[str, Any]:
  """Extract user status information from function arguments
  
  Args:
      args: Function positional arguments
      kwargs: Function keyword arguments
      
  Returns:
      Dict with status information
  """
  # Extract status information
  input_status = kwargs.get("input_status", {})
  new_status = getattr(input_status, "status", None)
  old_status = None

  # infer old status from the function args
  user_id = kwargs.get("user_id", None)
  if not user_id and len(args) > 0:
    user_id = args[0]

  if user_id:
    try:
      user = User.find_by_uuid(user_id)
      old_status = user.status
    except (ValueError, TypeError) as e:
      logger.debug(f"Invalid user_id format: {e}")
      old_status = "unknown"
    except AttributeError as e:
      logger.debug(f"User has no status attribute: {e}")
      old_status = "unknown"
    except KeyError as e:
      logger.debug(f"User not found: {e}")
      old_status = "unknown"

  return {
    "status_from": old_status or "unknown",
    "status_to": new_status or "unknown"
  }

def track_user_status_update(func: Callable):
  """Track user status update operations.
  
  Args:
      func: The function to track
      
  Returns:
      Wrapped function with tracking instrumentation
  """
  @wraps(func)
  async def async_wrapper(*args, **kwargs):
    # Extract status information
    status_info = extract_user_status_info(args, kwargs)
    status_from = status_info["status_from"]
    status_to = status_info["status_to"]

    # Start timing
    start_time = time.time()

    try:
      result = await func(*args, **kwargs)

      # Record metrics
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=status_from,
        status_to=status_to,
        result="success"
      ).inc()

      return result
    except Exception as e:
      # Log specific error types with appropriate levels
      if isinstance(e, (ValueError, TypeError)):
        logger.warning(f"Validation error in status update: {e}")
      elif isinstance(e, (KeyError, AttributeError)):
        logger.warning(f"Data error in status update: {e}")
      else:
        logger.error(f"Unexpected error in status update: {e}")

      # Record error metrics
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=status_from,
        status_to=status_to,
        result="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = measure_latency(
        start_time,
        "status_update",
        {
          "operation": "status_update", 
          "status_from": status_from,
          "status_to": status_to
        }
      )
      USER_OPERATION_LATENCY.labels(operation="status_update").observe(latency)

  @wraps(func)
  def sync_wrapper(*args, **kwargs):
    # Extract status information
    status_info = extract_user_status_info(args, kwargs)
    status_from = status_info["status_from"]
    status_to = status_info["status_to"]

    # Start timing
    start_time = time.time()

    try:
      result = func(*args, **kwargs)

      # Record metrics
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=status_from,
        status_to=status_to,
        result="success"
      ).inc()

      return result
    except Exception as e:
      # Log specific error types with appropriate levels
      if isinstance(e, (ValueError, TypeError)):
        logger.warning(f"Validation error in status update: {e}")
      elif isinstance(e, (KeyError, AttributeError)):
        logger.warning(f"Data error in status update: {e}")
      else:
        logger.error(f"Unexpected error in status update: {e}")

      # Record error metrics
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=status_from,
        status_to=status_to,
        result="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = measure_latency(
        start_time,
        "status_update",
        {
          "operation": "status_update", 
          "status_from": status_from,
          "status_to": status_to
        }
      )
      USER_OPERATION_LATENCY.labels(operation="status_update").observe(latency)

  # Return appropriate wrapper based on function type
  if asyncio.iscoroutinefunction(func):
    return async_wrapper
  else:
    return sync_wrapper

def extract_batch_size(result) -> int:
  """Extract batch size from import result
  
  Args:
      result: Function result
      
  Returns:
      int: Batch size extracted from result
  """
  batch_size = 0

  try:
    if isinstance(result, dict) and "data" in result:
      data = result["data"]
      if "created" in data and isinstance(data["created"], list):
        batch_size = len(data["created"])
      elif "users" in data and isinstance(data["users"], list):
        batch_size = len(data["users"])
      elif isinstance(data, list):
        batch_size = len(data)
  except (TypeError, AttributeError, KeyError):
    pass

  return batch_size

def track_user_import(func: Callable):
  """Track user import operations.
  
  Args:
      func: The function to track
      
  Returns:
      Wrapped function with tracking instrumentation
  """
  @wraps(func)
  async def async_wrapper(*args, **kwargs):
    # Get import method
    import_method = kwargs.get("import_method", "json")

    # Start timing
    start_time = time.time()

    try:
      result = await func(*args, **kwargs)

      # Try to get the batch size
      batch_size = extract_batch_size(result)

      # Record metrics
      if batch_size > 0:
        USER_IMPORT_BATCH_SIZE.observe(batch_size)

      USER_IMPORT_COUNT.labels(
        method=import_method,
        status="success"
      ).inc()

      return result
    except Exception as e:
      # Log specific error types with appropriate context
      error_type = type(e).__name__
      error_context = {"error_type": error_type, "error_message": str(e)}

      if isinstance(e, ValueError):
        logger.warning("Validation error in user import", extra=error_context)
      elif isinstance(e, (KeyError, AttributeError)):
        logger.warning("Data structure error in user import",
                        extra=error_context)
      elif isinstance(e, IOError):
        logger.warning("I/O error in user import", extra=error_context)
      elif isinstance(e, TypeError):
        logger.warning("Type error in user import", extra=error_context)
      else:
        logger.error("Unexpected error in user import", extra=error_context,
                      exc_info=True)

      # Record error metrics
      USER_IMPORT_COUNT.labels(
        method=import_method,
        status="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = measure_latency(
        start_time,
        "import_users",
        {"operation": "import_users", "import_method": import_method}
      )
      USER_OPERATION_LATENCY.labels(operation="import_users").observe(latency)

  @wraps(func)
  def sync_wrapper(*args, **kwargs):
    # Get import method
    import_method = kwargs.get("import_method", "json")

    # Start timing
    start_time = time.time()

    try:
      result = func(*args, **kwargs)

      # Try to get the batch size
      batch_size = extract_batch_size(result)

      # Record metrics
      if batch_size > 0:
        USER_IMPORT_BATCH_SIZE.observe(batch_size)

      USER_IMPORT_COUNT.labels(
        method=import_method,
        status="success"
      ).inc()

      # Log success with additional context
      logger.info(
        f"Successfully imported {batch_size} users via {import_method}",
        extra={
          "metric_type": "user_import_success",
          "import_method": import_method,
          "batch_size": batch_size
        }
      )

      return result
    except Exception as e:
      # Log specific error types with appropriate context
      error_type = type(e).__name__
      error_context = {
        "metric_type": "user_import_error",
        "error_type": error_type,
        "error_message": str(e)
      }

      if isinstance(e, ValueError):
        logger.warning("Validation error in user import",
                        extra=error_context)
      elif isinstance(e, (KeyError, AttributeError)):
        logger.warning("Data structure error in user import",
                        extra=error_context)
      elif isinstance(e, IOError):
        logger.warning("I/O error in user import", extra=error_context)
      elif isinstance(e, TypeError):
        logger.warning("Type error in user import", extra=error_context)
      else:
        error_context["error_class"] = error_type
        logger.error("Unexpected error in user import",
                      extra=error_context, exc_info=True)

      # Record error metrics
      USER_IMPORT_COUNT.labels(
        method=import_method,
        status="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = measure_latency(
        start_time,
        "import_users",
        {"operation": "import_users", "import_method": import_method}
      )
      USER_OPERATION_LATENCY.labels(operation="import_users").observe(latency)

  # Return appropriate wrapper based on function type
  if asyncio.iscoroutinefunction(func):
    return async_wrapper
  else:
    return sync_wrapper

# Convenience decorators for common operations
def track_create_user(func):
  """Track user creation operations."""
  return track_user_operation("create_user")(func)

def track_update_user(func):
  """Track user update operations."""
  return track_user_operation("update_user")(func)

def track_delete_user(func):
  """Track user deletion operations."""
  return track_user_operation("delete_user")(func)

def track_get_user(func):
  """Track user retrieval operations."""
  return track_user_operation("get_user")(func)

def track_list_users(func):
  """Track user listing operations."""
  return track_user_operation("list_users")(func)

def track_search_users(func):
  """Track user search operations."""
  return track_user_operation("search_users")(func)
