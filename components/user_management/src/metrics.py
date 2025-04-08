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
from typing import Callable
from common.models import User
from common.utils.logging_handler import Logger
from common.monitoring.metrics import (
  Counter,
  Histogram,
  Gauge,
  log_operation_result
)

# Initialize logger
logger = Logger.get_logger(__file__)

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

def track_user_operation(operation_type: str):
  """Decorator to track user management operations.
  
  Args:
      operation_type: Type of user operation
      
  Returns:
      Decorator function for the specified operation type
  """
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
        if operation_type == "create_user":
          USER_CREATE_COUNT.labels(status=status).inc()
        elif operation_type == "update_user":
          USER_UPDATE_COUNT.labels(status=status).inc()
        elif operation_type == "delete_user":
          USER_DELETE_COUNT.labels(status=status).inc()
        elif operation_type == "get_user":
          USER_GET_COUNT.labels(status=status).inc()
        elif operation_type.startswith("user_group_"):
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
        if operation_type == "create_user":
          USER_CREATE_COUNT.labels(status="error").inc()
        elif operation_type == "update_user":
          USER_UPDATE_COUNT.labels(status="error").inc()
        elif operation_type == "delete_user":
          USER_DELETE_COUNT.labels(status="error").inc()
        elif operation_type == "get_user":
          USER_GET_COUNT.labels(status="error").inc()
        elif operation_type.startswith("user_group_"):
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
        latency = time.time() - start_time
        USER_OPERATION_LATENCY.labels(
          operation=operation_type).observe(latency)

        # Log latency
        logger.info(
          f"{operation_type.replace('_', ' ').title()} operation latency",
          extra={
            "metric_type": "user_operation_latency",
            "operation": operation_type,
            "duration_ms": round(latency * 1000, 2)
          }
        )

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
        if operation_type == "create_user":
          USER_CREATE_COUNT.labels(status=status).inc()
        elif operation_type == "update_user":
          USER_UPDATE_COUNT.labels(status=status).inc()
        elif operation_type == "delete_user":
          USER_DELETE_COUNT.labels(status=status).inc()
        elif operation_type == "get_user":
          USER_GET_COUNT.labels(status=status).inc()
        elif operation_type.startswith("user_group_"):
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
        if operation_type == "create_user":
          USER_CREATE_COUNT.labels(status="error").inc()
        elif operation_type == "update_user":
          USER_UPDATE_COUNT.labels(status="error").inc()
        elif operation_type == "delete_user":
          USER_DELETE_COUNT.labels(status="error").inc()
        elif operation_type == "get_user":
          USER_GET_COUNT.labels(status="error").inc()
        elif operation_type.startswith("user_group_"):
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
        latency = time.time() - start_time
        USER_OPERATION_LATENCY.labels(
          operation=operation_type).observe(latency)

        # Log latency
        logger.info(
          f"{operation_type.replace('_', ' ').title()} operation latency",
          extra={
            "metric_type": "user_operation_latency",
            "operation": operation_type,
            "duration_ms": round(latency * 1000, 2)
          }
        )

        # Decrement concurrent operations
        CONCURRENT_OPERATIONS.labels(operation=operation_type).dec()

    # Return appropriate wrapper based on function type
    if asyncio.iscoroutinefunction(func):
      return async_wrapper
    else:
      return sync_wrapper

  return decorator

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

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      # Record metrics
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="success"
      ).inc()

      return result
    except (ValueError, TypeError) as e:
      logger.warning(f"Validation error in status update: {e}")
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="error"
      ).inc()
      raise
    except (KeyError, AttributeError) as e:
      logger.warning(f"Data error in status update: {e}")
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="error"
      ).inc()
      raise
    except Exception as e:
      logger.error(f"Unexpected error in status update: {e}")
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      USER_OPERATION_LATENCY.labels(
        operation="status_update").observe(latency)

      # Log latency
      logger.info(
        "User status update operation latency",
        extra={
          "metric_type": "user_operation_latency",
          "operation": "status_update",
          "duration_ms": round(latency * 1000, 2),
          "status_from": old_status,
          "status_to": new_status
        }
      )

  @wraps(func)
  def sync_wrapper(*args, **kwargs):
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

    start_time = time.time()
    try:
      result = func(*args, **kwargs)

      # Record metrics
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="success"
      ).inc()

      return result
    except (ValueError, TypeError) as e:
      logger.warning(f"Validation error in status update: {e}")
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="error"
      ).inc()
      raise
    except (KeyError, AttributeError) as e:
      logger.warning(f"Data error in status update: {e}")
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="error"
      ).inc()
      raise
    except Exception as e:
      logger.error(f"Unexpected error in status update: {e}")
      USER_STATUS_UPDATE_COUNT.labels(
        status_from=old_status or "unknown",
        status_to=new_status or "unknown",
        result="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      USER_OPERATION_LATENCY.labels(
        operation="status_update").observe(latency)

      # Log latency
      logger.info(
        "User status update operation latency",
        extra={
          "metric_type": "user_operation_latency",
          "operation": "status_update",
          "duration_ms": round(latency * 1000, 2),
          "status_from": old_status,
          "status_to": new_status
        }
      )

  # Return appropriate wrapper based on function type
  if asyncio.iscoroutinefunction(func):
    return async_wrapper
  else:
    return sync_wrapper

def track_user_import(func: Callable):
  """Track user import operations.
  
  Args:
      func: The function to track
      
  Returns:
      Wrapped function with tracking instrumentation
  """
  @wraps(func)
  async def async_wrapper(*args, **kwargs):
    start_time = time.time()

    try:
      result = await func(*args, **kwargs)

      import_method = kwargs.get("import_method", "json")

      # Try to get the batch size
      batch_size = 0
      if isinstance(result, dict) and "data" in result:
        data = result["data"]
        if "created" in data and isinstance(data["created"], list):
          batch_size = len(data["created"])
        elif "users" in data and isinstance(data["users"], list):
          batch_size = len(data["users"])

      # Record metrics
      if batch_size > 0:
        USER_IMPORT_BATCH_SIZE.observe(batch_size)

      USER_IMPORT_COUNT.labels(
        method=import_method,
        status="success"
      ).inc()

      return result
    except ValueError as e:
      logger.warning(f"Validation error in user import: {e}")
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    except (KeyError, AttributeError) as e:
      logger.warning(f"Data structure error in user import: {e}")
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    except IOError as e:
      logger.warning(f"I/O error in user import: {e}")
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    except Exception as e:
      logger.error(f"Unexpected error in user import: {e}", exc_info=True)
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      USER_OPERATION_LATENCY.labels(
        operation="import_users").observe(latency)

      # Log latency
      logger.info(
        "User import operation latency",
        extra={
          "metric_type": "user_operation_latency",
          "operation": "import_users",
          "duration_ms": round(latency * 1000, 2)
        }
      )

  @wraps(func)
  def sync_wrapper(*args, **kwargs):
    start_time = time.time()

    try:
      result = func(*args, **kwargs)

      import_method = kwargs.get("import_method", "json")

      # Try to get the batch size
      batch_size = 0
      if isinstance(result, dict) and "data" in result:
        data = result["data"]
        if "created" in data and isinstance(data["created"], list):
          batch_size = len(data["created"])
        elif "users" in data and isinstance(data["users"], list):
          batch_size = len(data["users"])
        elif isinstance(data, list):
          batch_size = len(data)

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
    except ValueError as e:
      # Validation errors (data doesn't match schema)
      logger.warning(
        f"Validation error in user import: {e}",
        extra={
          "metric_type": "user_import_error",
          "error_type": "validation_error",
          "error_message": str(e)
        }
      )
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    except (KeyError, AttributeError) as e:
      # Data structure errors (missing keys, wrong types)
      logger.warning(
        f"Data structure error in user import: {e}",
        extra={
          "metric_type": "user_import_error",
          "error_type": "data_structure_error",
          "error_message": str(e)
        }
      )
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    except IOError as e:
      # File handling errors
      logger.warning(
        f"I/O error in user import: {e}",
        extra={
          "metric_type": "user_import_error",
          "error_type": "io_error",
          "error_message": str(e)
        }
      )
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    except TypeError as e:
      # Type errors (wrong parameter types)
      logger.warning(
        f"Type error in user import: {e}",
        extra={
          "metric_type": "user_import_error",
          "error_type": "type_error",
          "error_message": str(e)
        }
      )
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    except Exception as e:
      # All other unexpected errors
      logger.error(
        f"Unexpected error in user import: {type(e).__name__}: {e}",
        extra={
          "metric_type": "user_import_error",
          "error_type": "unexpected_error",
          "error_class": type(e).__name__,
          "error_message": str(e)
        },
        exc_info=True
      )
      USER_IMPORT_COUNT.labels(
        method=kwargs.get("import_method", "json"),
        status="error"
      ).inc()
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      USER_OPERATION_LATENCY.labels(
        operation="import_users").observe(latency)

      # Log latency
      logger.info(
        "User import operation latency",
        extra={
          "metric_type": "user_operation_latency",
          "operation": "import_users",
          "duration_ms": round(latency * 1000, 2),
          "import_method": kwargs.get("import_method", "json")
        }
      )

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
