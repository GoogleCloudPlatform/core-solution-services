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
from typing import Callable, Dict, Any

from common.monitoring.metrics import (
  Counter, Histogram, Gauge,
  extract_user_id, log_operation_result,
  safe_extract_config_dict, measure_latency,
  track_streaming_response_size, record_response_size,
  record_user_activity, create_decorator_for_streaming_func
)
from common.utils.logging_handler import Logger
from common.models import QueryEngine

# Initialize logger
logger = Logger.get_logger("llm_service.metrics")

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
  ["llm_type"], buckets=[10, 50, 100, 500, 1000,
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
    64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
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


def extract_llm_params(kwargs: Dict[str, Any]) -> Dict[str, Any]:
  """Extract LLM parameters from kwargs
  
  Args:
      kwargs: Keyword arguments
      
  Returns:
      Dict with LLM parameters
  """
  gen_config = kwargs.get("gen_config")
  config_dict = safe_extract_config_dict(gen_config)

  llm_type = config_dict.get("llm_type", "unknown")
  prompt = config_dict.get("prompt", "")
  prompt_size = len(prompt)

  # Record prompt size
  if prompt_size > 0:
    PROMPT_SIZE.labels("llm").observe(prompt_size)

  return {
    "llm_type": llm_type,
    "prompt_size": prompt_size
  }


def extract_embedding_params(kwargs: Dict[str, Any]) -> Dict[str, Any]:
  """Extract embedding parameters from kwargs
  
  Args:
      kwargs: Keyword arguments
      
  Returns:
      Dict with embedding parameters
  """
  embedding_config = kwargs.get("embeddings_config")
  config_dict = safe_extract_config_dict(embedding_config)

  embedding_type = config_dict.get("embedding_type", "unknown")
  text = config_dict.get("text", "")
  text_size = len(text)

  # Record text size
  if text_size > 0:
    PROMPT_SIZE.labels("embedding").observe(text_size)

  return {
    "embedding_type": embedding_type,
    "text_size": text_size
  }


def extract_chat_params(kwargs: Dict[str, Any]) -> Dict[str, Any]:
  """Extract chat parameters from kwargs
  
  Args:
      kwargs: Keyword arguments
      
  Returns:
      Dict with chat parameters
  """
  gen_config = kwargs.get("gen_config")

  # Initialize defaults
  params = {
    "llm_type": "unknown",
    "with_file": False,
    "with_tools": False,
    "prompt_size": 0,
    "is_streaming": False
  }

  try:
    if not gen_config:
      # For create_user_chat function
      prompt = kwargs.get("prompt", "")
      params["llm_type"] = kwargs.get("llm_type", "unknown")
      params["with_file"] = (kwargs.get("chat_file") is not None or
                            kwargs.get("chat_file_url") is not None)
      params["with_tools"] = kwargs.get("tool_names") is not None
      params["is_streaming"] = kwargs.get("stream", False)
      params["prompt_size"] = len(prompt) if prompt else 0
    else:
      # For other chat functions with gen_config
      config_dict = safe_extract_config_dict(gen_config)

      params["llm_type"] = config_dict.get("llm_type", "unknown")
      params["with_file"] = (config_dict.get("chat_file_b64") is not None or
                           config_dict.get("chat_file_url") is not None)
      params["with_tools"] = config_dict.get("tool_names") is not None
      params["is_streaming"] = config_dict.get("stream", False)
      params["prompt_size"] = len(config_dict.get("prompt", ""))
  except Exception as e:
    logger.error(f"Error extracting chat parameters: {type(e).__name__}: {e}")
    raise

  # Record prompt size metric
  if params["prompt_size"] > 0:
    PROMPT_SIZE.labels("chat").observe(params["prompt_size"])

  return params


def get_query_engine_info(query_engine_id: str) -> Dict[str, str]:
  """Get query engine information by ID
  
  Args:
      query_engine_id: The ID of the query engine
      
  Returns:
      Dict with db_type and engine_name
  """
  info = {
    "db_type": "unknown",
    "engine_name": "unknown"
  }

  if not query_engine_id:
    return info

  try:
    q_engine = QueryEngine.find_by_id(query_engine_id)
    if q_engine:
      info["db_type"] = q_engine.vector_store or "unknown"
      info["engine_name"] = q_engine.name or "unknown"
  except Exception as e:
    logger.error(f"Error extracting vector DB info: {type(e).__name__}: {e}")
    raise

  return info


# Create LLM generation decorator
track_llm_generate = create_decorator_for_streaming_func(
  count_metric=LLM_GENERATE_COUNT,
  latency_metric=LLM_GENERATE_LATENCY,
  response_size_metric=LLM_RESPONSE_SIZE,
  activity_counter=USER_ACTIVITY,
  activity_type="llm_generation",
  metric_name="llm_generation",
  extract_labels_func=extract_llm_params
)


# Create embedding generation decorator
track_embedding_generate = create_decorator_for_streaming_func(
  count_metric=EMBEDDING_GENERATE_COUNT,
  latency_metric=EMBEDDING_GENERATE_LATENCY,
  activity_counter=USER_ACTIVITY,
  activity_type="embedding_generation",
  metric_name="embedding_generation",
  extract_labels_func=extract_embedding_params
)


def track_chat_generate(func: Callable):
  """Decorator to track chat generation metrics including response size"""

  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract parameters
    params = extract_chat_params(kwargs)
    llm_type = params["llm_type"]
    with_file = params["with_file"]
    with_tools = params["with_tools"]
    prompt_size = params["prompt_size"]
    is_streaming = params["is_streaming"]

    # Extract user information and record activity
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "chat_generation", USER_ACTIVITY)

    # Start timing
    start_time = time.time()

    try:
      # Call original function
      result = await func(*args, **kwargs)

      # Format labels for metrics
      str_with_file = str(with_file)
      str_with_tools = str(with_tools)

      # Handle streaming vs non-streaming results for size tracking
      if asyncio.iscoroutine(result) or inspect.isasyncgen(result):
        extra_data = {
          "with_file": with_file,
          "with_tools": with_tools
        }
        result = await track_streaming_response_size(
          generator=result,
          response_size_metric=LLM_RESPONSE_SIZE,
          metric_type=llm_type,
          extra_data=extra_data
        )
      else:
        # Record size for non-streaming
        record_response_size(
          result,
          LLM_RESPONSE_SIZE,
          llm_type,
          {"with_file": with_file, "with_tools": with_tools}
        )

      # Track chat history size if available
      history_size = None
      if isinstance(
        result, dict) and "data" in result and "history" in result["data"]:
        history_size = len(result["data"]["history"])
        CHAT_HISTORY_SIZE.labels(llm_type=llm_type).observe(history_size)

      # Record success metrics
      CHAT_GENERATE_COUNT.labels(
        llm_type=llm_type,
        with_file=str_with_file,
        with_tools=str_with_tools,
        status="success",
        user_id=user_id
      ).inc()

      # Log success
      log_extra = {
        "llm_type": llm_type,
        "with_file": with_file,
        "with_tools": with_tools,
        "prompt_size": prompt_size,
        "user_id": user_id,
        "response_size": "streaming" if is_streaming else "done"
      }

      if history_size is not None:
        log_extra["history_size"] = history_size

      log_operation_result(logger, "chat_generation", "success", log_extra)

      return result

    except Exception as e:
      # Record error metrics
      CHAT_GENERATE_COUNT.labels(
        llm_type=llm_type,
        with_file=str_with_file,
        with_tools=str_with_tools,
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
      latency = measure_latency(
        start_time,
        "chat_generation",
        {
          "llm_type": llm_type,
          "with_file": with_file,
          "with_tools": with_tools
        }
      )
      CHAT_GENERATE_LATENCY.labels(
        llm_type=llm_type,
        with_file=str(with_file),
        with_tools=str(with_tools)
      ).observe(latency)

  return wrapper


def track_chat_operations(func: Callable) -> Callable:
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

      if isinstance(result, dict) and result.get("success"):
        # Handle chat creation
        if "create" in func_name:
          ACTIVE_CHATS_TOTAL.labels(user_id=user_id).inc()
          record_user_activity(user_id, "chat_create", USER_ACTIVITY)
          log_operation_result(
            logger, "chat_creation", "success", {"user_id": user_id}
          )

        # Handle chat deletion
        elif "delete" in func_name:
          ACTIVE_CHATS_TOTAL.labels(user_id=user_id).dec()
          record_user_activity(user_id, "chat_delete", USER_ACTIVITY)
          log_operation_result(
            logger, "chat_deletion", "success", {"user_id": user_id}
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

      if isinstance(result, dict) and result.get("success"):
        # Handle chat creation
        if "create" in func_name:
          ACTIVE_CHATS_TOTAL.labels(user_id=user_id).inc()
          record_user_activity(user_id, "chat_create", USER_ACTIVITY)
          log_operation_result(
            logger, "chat_creation", "success", {"user_id": user_id}
          )

        # Handle chat deletion
        elif "delete" in func_name:
          ACTIVE_CHATS_TOTAL.labels(user_id=user_id).dec()
          record_user_activity(user_id, "chat_delete", USER_ACTIVITY)
          log_operation_result(
            logger, "chat_deletion", "success", {"user_id": user_id}
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

    # Extract user information and record activity
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "agent_execution", USER_ACTIVITY)

    # Start timing
    start_time = time.time()

    try:
      # Call the original function
      result = await func(*args, **kwargs)

      # Record success metrics
      AGENT_EXECUTION_COUNT.labels(
        agent_type=agent_type,
        status="success"
      ).inc()

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
      AGENT_EXECUTION_COUNT.labels(
        agent_type=agent_type,
        status="error"
      ).inc()

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
      latency = measure_latency(
        start_time,
        "agent_execution",
        {"agent_type": agent_type, "agent_name": agent_name}
      )
      AGENT_EXECUTION_LATENCY.labels(agent_type=agent_type).observe(latency)

  return wrapper


def track_vector_db_query(func: Callable):
  """Decorator to track vector database query metrics"""

  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract vector DB information
    query_engine_id = kwargs.get("query_engine_id")
    if not query_engine_id and args:
      query_engine_id = args[0] if args else None

    engine_info = get_query_engine_info(query_engine_id)
    db_type = engine_info["db_type"]
    engine_name = engine_info["engine_name"]

    # Extract user information and record activity
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "vector_db_query", USER_ACTIVITY)

    # Start timing
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
      latency = measure_latency(
        start_time,
        "vector_db_query",
        {"db_type": db_type, "engine_name": engine_name}
      )
      VECTOR_DB_QUERY_LATENCY.labels(
        db_type=db_type,
        engine_name=engine_name
      ).observe(latency)

  return wrapper


def track_vector_db_build(func: Callable):
  """Decorator to track vector database build metrics"""

  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract vector DB information from config
    gen_config = kwargs.get("gen_config")
    config_dict = safe_extract_config_dict(gen_config)

    db_type = config_dict.get("vector_store", "unknown")
    engine_name = config_dict.get("query_engine", "unknown")

    # Extract user information and record activity
    user_data = kwargs.get("user_data")
    user_id = extract_user_id(user_data)
    if user_id != "unknown":
      record_user_activity(user_id, "vector_db_build", USER_ACTIVITY)

    # Start timing
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
      latency = measure_latency(
        start_time,
        "vector_db_build",
        {"db_type": db_type, "engine_name": engine_name}
      )
      VECTOR_DB_BUILD_LATENCY.labels(
        db_type=db_type,
        engine_name=engine_name
      ).observe(latency)

  return wrapper


# Convenience function aliases for better readability
track_llm = track_llm_generate
track_embedding = track_embedding_generate
track_chat = track_chat_generate
track_agent = track_agent_execution
track_vector_query = track_vector_db_query
track_vector_build = track_vector_db_build
