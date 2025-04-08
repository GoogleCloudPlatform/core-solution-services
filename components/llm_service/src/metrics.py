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

"""LLM service-specific metrics and tracking decorators"""

import time
import asyncio
import inspect
from functools import wraps
from typing import Callable
from common.monitoring.metrics import Counter, Histogram, Gauge
from common.utils.logging_handler import Logger
from common.monitoring.metrics import extract_user_id, log_operation_result
from common.models import QueryEngine

# Initialize logger
logger = Logger.get_logger(__file__)

# LLM Generation Metrics
LLM_GENERATE_COUNT = Counter(
  "llm_generate_count", "LLM Generation Count",
  ["llm_type", "status"]
)

LLM_GENERATE_LATENCY = Histogram(
  "llm_generate_latency_seconds", "LLM Generation Latency",
  ["llm_type"]
)

# Response size
LLM_RESPONSE_SIZE = Histogram(
  "llm_response_size_chars", "LLM Response Size in Characters",
  ["llm_type"], buckets=[10, 50, 100, 500, 1000,\
                          2000, 5000, 10000, 20000, 50000]
)

# Embedding Metrics
EMBEDDING_GENERATE_COUNT = Counter(
  "embedding_generate_count", "Embedding Generation Count",
  ["embedding_type", "status"]
)

EMBEDDING_GENERATE_LATENCY = Histogram(
  "embedding_generate_latency_seconds", "Embedding Generation Latency",
  ["embedding_type"]
)

# Chat Metrics
CHAT_GENERATE_COUNT = Counter(
  "chat_generate_count", "Chat Generation Count",
  ["llm_type", "with_file", "with_tools", "status", "user_id"]
)

CHAT_GENERATE_LATENCY = Histogram(
  "chat_generate_latency_seconds", "Chat Generation Latency",
  ["llm_type", "with_file", "with_tools"]
)

CHAT_HISTORY_SIZE = Histogram(
  "chat_history_size", "Number of Entries in Chat History",
  ["llm_type"], buckets=[1, 2, 5, 10, 15, 20, 30, 50, 100]
)

ACTIVE_CHATS_TOTAL = Gauge(
  "active_chats_total", "Total Active Chats",
  ["user_id"]
)

# User Activity Metrics
USER_ACTIVITY = Counter(
  "user_activity", "User Activity Counter",
  ["user_id", "activity_type"]
)

# Active Users Gauge
ACTIVE_USERS = Gauge(
  "active_users", "Number of Active Users",
  ["time_window"]
)

# Prompt size
PROMPT_SIZE = Histogram(
  "prompt_size_bytes", "Prompt Size in Bytes",
  ["type"], buckets=[
    64, 128, 256, 512, 1024, 2048, 4096,8192, 16384, 32768, 65536]
)

# Agent Metrics
AGENT_EXECUTION_COUNT = Counter(
  "agent_execution_count", "Agent Execution Count",
  ["agent_type", "status"]
)

AGENT_EXECUTION_LATENCY = Histogram(
  "agent_execution_latency_seconds", "Agent Execution Latency",
  ["agent_type"]
)

TOOLS_USAGE_COUNT = Counter(
  "tools_usage_count", "Number of Times Each Tool Is Used",
  ["tool_name"]
)

# Vector DB Metrics
VECTOR_DB_QUERY_COUNT = Counter(
  "vector_db_query_count", "Vector Database Query Count",
  ["db_type", "engine_name", "status"]
)

VECTOR_DB_QUERY_LATENCY = Histogram(
  "vector_db_query_latency_seconds", "Vector Database Query Latency",
  ["db_type", "engine_name"]
)

VECTOR_DB_BUILD_COUNT = Counter(
  "vector_db_build_count", "Vector Database Build Count",
  ["db_type", "engine_name", "status"]
)

VECTOR_DB_BUILD_LATENCY = Histogram(
  "vector_db_build_latency_seconds", "Vector Database Build Latency",
  ["db_type", "engine_name"]
)

VECTOR_DB_DOC_COUNT = Histogram(
  "vector_db_doc_count", "Number of Documents in Vector DB",
  ["db_type", "engine_name"], buckets=[
    10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]
)

def record_user_activity(user_id: str, activity_type: str):
  """Record user activity for tracking active users
  
  Args:
      user_id: The user's ID (usually email)
      activity_type: Type of activity (e.g., 'chat', 'query', 'login')
  """
  if user_id and user_id != "unknown":
    USER_ACTIVITY.labels(
      user_id=user_id,
      activity_type=activity_type
    ).inc()

def _extract_config_dict(config):
  """Extract dictionary from config object in a consistent way
  
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
  except TypeError as e:
    logger.error(f"Type error extracting config dictionary: {e}")
    return {}
  except AttributeError as e:
    logger.error(f"Attribute error extracting config dictionary: {e}")
    return {}
  except ValueError as e:
    logger.error(f"Value error extracting config dictionary: {e}")
    return {}
  except KeyError as e:
    logger.error(f"Key error extracting config dictionary: {e}")
    return {}

def track_llm_generate(func: Callable):
  """Decorator to track LLM generation metrics including response size"""

  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract llm_type
    gen_config = kwargs.get("gen_config")
    config_dict = _extract_config_dict(gen_config)

    llm_type = config_dict.get("llm_type", "unknown")
    prompt = config_dict.get("prompt", "")
    prompt_size = len(prompt)

    if prompt_size > 0:
      PROMPT_SIZE.labels("llm").observe(prompt_size)

    # Extract user information
    user_data = kwargs.get("user_data", None)
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "llm_generation")

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      # Handle streaming vs non-streaming responses for size metrics
      if inspect.isasyncgen(result):
        # For streaming responses, wrap the generator to count characters
        original_result = result

        async def size_tracking_generator():
          total_chars = 0
          async for chunk in original_result:
            if isinstance(chunk, str):
              total_chars += len(chunk)
            yield chunk

          # Log the total response size after streaming completes
          logger.info(
            "LLM response size",
            extra={
              "metric_type": "llm_response_size",
              "llm_type": llm_type,
              "is_streaming": True,
              "response_size_chars": total_chars
            }
          )

          # Record response size in histogram
          LLM_RESPONSE_SIZE.labels(llm_type=llm_type).observe(total_chars)

        # Return the wrapped generator
        result = size_tracking_generator()
      elif isinstance(result, str):
        # For direct string responses, measure size immediately
        response_size = len(result)
        logger.info(
          "LLM response size",
          extra={
            "metric_type": "llm_response_size",
            "llm_type": llm_type,
            "is_streaming": False,
            "response_size_chars": response_size
          }
        )
        LLM_RESPONSE_SIZE.labels(llm_type=llm_type).observe(response_size)
      elif isinstance(result, dict) and "content" in result:
        # For dictionary responses with content field
        response_size = len(result["content"])\
            if isinstance(result["content"], str) else 0
        logger.info(
          "LLM response size",
          extra={
            "metric_type": "llm_response_size",
            "llm_type": llm_type,
            "is_streaming": False,
            "response_size_chars": response_size
          }
        )
        LLM_RESPONSE_SIZE.labels(llm_type=llm_type).observe(response_size)

      # Record success metrics
      LLM_GENERATE_COUNT.labels(llm_type=llm_type, status="success").inc()

      # Log success
      log_operation_result(
        logger,
        "llm_generation",
        "success",
        {
          "llm_type": llm_type,
          "prompt_size": prompt_size
        }
      )

      return result
    except Exception as e:
      # Record error metrics
      LLM_GENERATE_COUNT.labels(llm_type=llm_type, status="error").inc()

      # Log error
      log_operation_result(
        logger,
        "llm_generation",
        "error",
        {
          "llm_type": llm_type,
          "prompt_size": prompt_size,
          "error_message": str(e)
        }
      )
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      LLM_GENERATE_LATENCY.labels(llm_type=llm_type).observe(latency)

      # Log latency
      logger.info(
        "LLM generation latency",
        extra={
          "metric_type": "llm_generation_latency",
          "llm_type": llm_type,
          "duration_ms": round(latency * 1000, 2)
        }
      )
  return wrapper

def track_embedding_generate(func: Callable):
  """Decorator to track embedding generation metrics"""
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract embedding configuration
    embedding_config = kwargs.get("embeddings_config")
    config_dict = _extract_config_dict(embedding_config)

    embedding_type = config_dict.get("embedding_type", "unknown")
    text = config_dict.get("text", "")
    text_size = len(text)

    if text_size > 0:
      PROMPT_SIZE.labels("embedding").observe(text_size)

    # Extract user information
    user_data = kwargs.get("user_data", None)
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "embedding_generation")

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      # Record success metrics
      EMBEDDING_GENERATE_COUNT.labels(embedding_type=embedding_type,\
                                       status="success").inc()

      # Log success
      log_operation_result(
        logger,
        "embedding_generation",
        "success",
        {
          "embedding_type": embedding_type,
          "text_size": text_size
        }
      )

      return result
    except Exception as e:
      # Record error metrics
      EMBEDDING_GENERATE_COUNT.labels(embedding_type=embedding_type,\
                                       status="error").inc()

      # Log error
      log_operation_result(
        logger,
        "embedding_generation",
        "error",
        {
          "embedding_type": embedding_type,
          "text_size": text_size,
          "error_message": str(e)
        }
      )
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      EMBEDDING_GENERATE_LATENCY.labels(
        embedding_type=embedding_type).observe(latency)

      # Log latency
      logger.info(
        "Embedding generation latency",
        extra={
          "metric_type": "embedding_generation_latency",
          "embedding_type": embedding_type,
          "duration_ms": round(latency * 1000, 2)
        }
      )
  return wrapper

def track_chat_generate(func: Callable):
  """Decorator to track chat generation metrics including response size"""
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract parameters
    gen_config = kwargs.get("gen_config")

    # Initialize defaults
    llm_type = "unknown"
    with_file = False
    with_tools = False
    prompt_size = 0

    # Extract user information
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "chat_generation")

    try:
      # Extract chat parameters based on input pattern
      if not gen_config:
        # For create_user_chat function
        prompt = kwargs.get("prompt", "")
        llm_type = kwargs.get("llm_type", "unknown")
        chat_file = kwargs.get("chat_file")
        chat_file_url = kwargs.get("chat_file_url")
        tool_names = kwargs.get("tool_names")

        with_file = (chat_file is not None or chat_file_url is not None)
        with_tools = tool_names is not None
        prompt_size = len(prompt) if prompt else 0
      else:
        # For other chat functions with gen_config
        config_dict = _extract_config_dict(gen_config)

        llm_type = config_dict.get("llm_type", "unknown")
        prompt = config_dict.get("prompt", "")
        with_file = (config_dict.get("chat_file_b64") is not None or
                    config_dict.get("chat_file_url") is not None)
        with_tools = config_dict.get("tool_names") is not None
        prompt_size = len(prompt)

      # Record prompt size metric
      if prompt_size > 0:
        PROMPT_SIZE.labels("chat").observe(prompt_size)
    except TypeError as e:
      # Handle type errors (wrong parameter types)
      log_operation_result(
        logger,
        "chat_parameters_extraction",
        "error",
        {
          "error_type": "TypeError",
          "error_message": str(e)
        }
      )
    except AttributeError as e:
      # Handle attribute errors (missing attributes)
      log_operation_result(
        logger,
        "chat_parameters_extraction",
        "error",
        {
          "error_type": "AttributeError",
          "error_message": str(e)
        }
      )
    except KeyError as e:
      # Handle key errors (missing dictionary keys)
      log_operation_result(
        logger,
        "chat_parameters_extraction",
        "error",
        {
          "error_type": "KeyError",
          "error_message": str(e)
        }
      )
    except ValueError as e:
      # Handle value errors (invalid values)
      log_operation_result(
        logger,
        "chat_parameters_extraction",
        "error",
        {
          "error_type": "ValueError",
          "error_message": str(e)
        }
      )

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      # Handle streaming vs non-streaming results for response size tracking
      if asyncio.iscoroutine(result) or inspect.isasyncgen(result):
        # For streaming responses, wrap the generator to count characters
        original_result = result

        async def size_tracking_generator():
          total_chars = 0
          async for chunk in original_result:
            total_chars += len(chunk) if isinstance(chunk, str) else 0
            yield chunk

          # Log the total response size after all chunks are processed
          logger.info(
            "LLM response size",
            extra={
              "metric_type": "llm_response_size",
              "llm_type": llm_type,
              "with_file": with_file,
              "with_tools": with_tools,
              "is_streaming": True,
              "response_size_chars": total_chars
            }
          )

          # Create a histogram of response sizes
          LLM_RESPONSE_SIZE.labels(llm_type=llm_type).observe(total_chars)

        # Replace the result with our tracking generator
        result = size_tracking_generator()
      elif isinstance(result, str):
        # For direct string responses, measure size immediately
        response_size = len(result)
        logger.info(
          "LLM response size",
          extra={
            "metric_type": "llm_response_size",
            "llm_type": llm_type,
            "with_file": with_file,
            "with_tools": with_tools,
            "is_streaming": False,
            "response_size_chars": response_size
          }
        )
        LLM_RESPONSE_SIZE.labels(llm_type=llm_type).observe(response_size)

      # Record success metrics
      CHAT_GENERATE_COUNT.labels(
        llm_type=llm_type,
        with_file=str(with_file),
        with_tools=str(with_tools),
        status="success",
        user_id=user_id
      ).inc()

      # Prepare additional data for logging
      log_extra = {
        "llm_type": llm_type,
        "with_file": with_file,
        "with_tools": with_tools,
        "prompt_size": prompt_size,
        "user_id": user_id
      }

      # Track chat history size if available
      if isinstance(result, dict) and "data"\
          in result and "history" in result["data"]:
        history_size = len(result["data"]["history"])
        CHAT_HISTORY_SIZE.labels(llm_type=llm_type).observe(history_size)
        log_extra["history_size"] = history_size

      # Log success
      log_operation_result(
        logger,
        "chat_generation",
        "success",
        log_extra
      )

      return result
    except Exception as e:
      # Record error metrics
      CHAT_GENERATE_COUNT.labels(
        llm_type=llm_type,
        with_file=str(with_file),
        with_tools=str(with_tools),
        status="error",
        user_id=user_id
      ).inc()

      # Log error
      log_operation_result(
        logger,
        "chat_generation",
        "error",
        {
          "llm_type": llm_type,
          "with_file": with_file,
          "with_tools": with_tools,
          "prompt_size": prompt_size,
          "user_id": user_id,
          "error_message": str(e)
        }
      )
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      CHAT_GENERATE_LATENCY.labels(
        llm_type=llm_type,
        with_file=str(with_file),
        with_tools=str(with_tools)
      ).observe(latency)

      # Log latency
      logger.info(
        "Chat generation latency",
        extra={
          "metric_type": "chat_generation_latency",
          "llm_type": llm_type,
          "with_file": with_file,
          "with_tools": with_tools,
          "duration_ms": round(latency * 1000, 2)
        }
      )
  return wrapper

def track_chat_operations(func: Callable):
  """Decorator to track chat operations (create, delete, etc.)"""
  @wraps(func)
  async def async_wrapper(*args, **kwargs):
    # Extract user information
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)

    try:
      result = await func(*args, **kwargs)

      # Check operation type from function name
      func_name = func.__name__

      # Handle chat creation
      if "create" in func_name and isinstance(result, dict)\
          and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).inc()
        record_user_activity(user_id, "chat_create")

        log_operation_result(
          logger,
          "chat_creation",
          "success",
          {"user_id": user_id}
        )

      # Handle chat deletion
      if "delete" in func_name and isinstance(result, dict)\
          and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).dec()
        record_user_activity(user_id, "chat_delete")

        log_operation_result(
          logger,
          "chat_deletion",
          "success",
          {"user_id": user_id}
        )

      return result
    except Exception as e:
      # Log error
      log_operation_result(
        logger,
        "chat_operation",
        "error",
        {
          "operation": func.__name__,
          "user_id": user_id,
          "error_message": str(e)
        }
      )
      raise

  @wraps(func)
  def sync_wrapper(*args, **kwargs):
    # Extract user information
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)

    try:
      result = func(*args, **kwargs)

      # Check operation type from function name
      func_name = func.__name__

      # Handle chat creation
      if "create" in func_name and isinstance(result, dict)\
          and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).inc()
        record_user_activity(user_id, "chat_create")

        log_operation_result(
          logger,
          "chat_creation",
          "success",
          {"user_id": user_id}
        )

      # Handle chat deletion
      if "delete" in func_name and isinstance(result, dict)\
          and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).dec()
        record_user_activity(user_id, "chat_delete")

        log_operation_result(
          logger,
          "chat_deletion",
          "success",
          {"user_id": user_id}
        )

      return result
    except Exception as e:
      # Log error
      log_operation_result(
        logger,
        "chat_operation",
        "error",
        {
          "operation": func.__name__,
          "user_id": user_id,
          "error_message": str(e)
        }
      )
      raise

  # Return appropriate wrapper based on function type
  if asyncio.iscoroutinefunction(func):
    return async_wrapper
  else:
    return sync_wrapper

def track_agent_execution(func: Callable):
  """Decorator to track agent execution metrics"""
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract agent information
    agent_type = kwargs.get("agent_type", "unknown")
    agent_name = kwargs.get("agent_name", "unknown")

    # Extract user information
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "agent_execution")

    start_time = time.time()
    try:
      # Call the original function
      result = await func(*args, **kwargs)

      # Record success metrics
      AGENT_EXECUTION_COUNT.labels(agent_type=agent_type,\
                                    status="success").inc()

      # Log success
      log_operation_result(
        logger,
        "agent_execution",
        "success",
        {
          "agent_type": agent_type,
          "agent_name": agent_name
        }
      )

      return result
    except Exception as e:
      # Record error metrics
      AGENT_EXECUTION_COUNT.labels(agent_type=agent_type,\
                                    status="error").inc()

      # Log error
      log_operation_result(
        logger,
        "agent_execution",
        "error",
        {
          "agent_type": agent_type,
          "agent_name": agent_name,
          "error_message": str(e)
        }
      )
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      AGENT_EXECUTION_LATENCY.labels(
        agent_type=agent_type).observe(latency)

      # Log latency
      logger.info(
        "Agent execution latency",
        extra={
          "metric_type": "agent_execution_latency",
          "agent_type": agent_type,
          "agent_name": agent_name,
          "duration_ms": round(latency * 1000, 2)
        }
      )
  return wrapper

def track_vector_db_query(func: Callable):
  """Decorator to track vector database query metrics"""
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract vector DB information
    query_engine_id = kwargs.get("query_engine_id") or args[0]
    db_type = "unknown"
    engine_name = "unknown"

    try:
      # Try to get the QueryEngine object to extract relevant metadata
      if query_engine_id:
        q_engine = QueryEngine.find_by_id(query_engine_id)
        if q_engine:
          db_type = q_engine.vector_store or "unknown"
          engine_name = q_engine.name or "unknown"
    except AttributeError as e:
      # Handle attribute errors (missing attributes on QueryEngine)
      logger.error(f"Attribute error extracting vector DB info: {str(e)}")
    except KeyError as e:
      # Handle key errors (missing dict keys)
      logger.error(f"Key error extracting vector DB info: {str(e)}")
    except ValueError as e:
      # Handle value errors (invalid ID format)
      logger.error(f"Value error extracting vector DB info: {str(e)}")
    except TypeError as e:
      # Handle type errors (wrong parameter types)
      logger.error(f"Type error extracting vector DB info: {str(e)}")

    # Extract user information
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "vector_db_query")

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      # Record success metrics
      VECTOR_DB_QUERY_COUNT.labels(
        db_type=db_type,
        engine_name=engine_name,
        status="success"
      ).inc()

      # Log success
      log_operation_result(
        logger,
        "vector_db_query",
        "success",
        {
          "db_type": db_type,
          "engine_name": engine_name
        }
      )

      return result
    except Exception as e:
      # Record error metrics
      VECTOR_DB_QUERY_COUNT.labels(
        db_type=db_type,
        engine_name=engine_name,
        status="error"
      ).inc()

      # Log error
      log_operation_result(
        logger,
        "vector_db_query",
        "error",
        {
          "db_type": db_type,
          "engine_name": engine_name,
          "error_message": str(e)
        }
      )
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      VECTOR_DB_QUERY_LATENCY.labels(
        db_type=db_type,
        engine_name=engine_name
      ).observe(latency)

      # Log latency
      logger.info(
        "Vector DB query latency",
        extra={
          "metric_type": "vector_db_query_latency",
          "db_type": db_type,
          "engine_name": engine_name,
          "duration_ms": round(latency * 1000, 2)
        }
      )
  return wrapper

def track_vector_db_build(func: Callable):
  """Decorator to track vector database build metrics"""
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract vector DB information from config
    gen_config = kwargs.get("gen_config")
    config_dict = _extract_config_dict(gen_config)

    db_type = config_dict.get("vector_store", "unknown")
    engine_name = config_dict.get("query_engine", "unknown")

    # Extract user information
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "vector_db_build")

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      # Record success metrics
      VECTOR_DB_BUILD_COUNT.labels(
        db_type=db_type,
        engine_name=engine_name,
        status="success"
      ).inc()

      # Log success
      log_operation_result(
        logger,
        "vector_db_build",
        "success",
        {
          "db_type": db_type,
          "engine_name": engine_name
        }
      )

      return result
    except Exception as e:
      # Record error metrics
      VECTOR_DB_BUILD_COUNT.labels(
        db_type=db_type,
        engine_name=engine_name,
        status="error"
      ).inc()

      # Log error
      log_operation_result(
        logger,
        "vector_db_build",
        "error",
        {
          "db_type": db_type,
          "engine_name": engine_name,
          "error_message": str(e)
        }
      )
      raise
    finally:
      # Record latency
      latency = time.time() - start_time
      VECTOR_DB_BUILD_LATENCY.labels(
        db_type=db_type,
        engine_name=engine_name
      ).observe(latency)

      # Log latency
      logger.info(
        "Vector DB build latency",
        extra={
          "metric_type": "vector_db_build_latency",
          "db_type": db_type,
          "engine_name": engine_name,
          "duration_ms": round(latency * 1000, 2)
        }
      )
  return wrapper

# Convenience function aliases for better readability
track_llm = track_llm_generate
track_embedding = track_embedding_generate
track_chat = track_chat_generate
track_agent = track_agent_execution
track_vector_query = track_vector_db_query
track_vector_build = track_vector_db_build
