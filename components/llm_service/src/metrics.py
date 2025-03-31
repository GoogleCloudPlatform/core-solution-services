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

"""Prometheus metrics and instrumentation for the LLM Service"""

import time
import asyncio
import logging
import json
from typing import Callable, Optional, Dict, Any, Union
from functools import wraps
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Request, Response
from fastapi.routing import APIRouter
from starlette.middleware.base import BaseHTTPMiddleware
from common.models import QueryEngine

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

# LLM Generation Metrics
LLM_GENERATE_COUNT = Counter(
  "llm_generate_count", "LLM Generation Count",
  ["llm_type", "status"]
)

LLM_GENERATE_LATENCY = Histogram(
  "llm_generate_latency_seconds", "LLM Generation Latency",
  ["llm_type"]
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

# Active Users Gauge (can be set to current count of active users)
ACTIVE_USERS = Gauge(
  "active_users", "Number of Active Users",
  ["time_window"]
)

# Prompt size
PROMPT_SIZE = Histogram(
  "prompt_size_bytes", "Prompt Size in Bytes",
  ["type"], buckets=[64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536]
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
  ["db_type", "engine_name"], buckets=[10, 50, 100, 500, 1000, 5000, 10000, 50000, 100000]
)

class PrometheusMiddleware(BaseHTTPMiddleware):
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
        "llm_service", method, path
      ).observe(request_latency)

      REQUEST_COUNT.labels(
        "llm_service", method, path, response.status_code
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

      return response
    except Exception as e:
      error_type = type(e).__name__
      ERROR_COUNT.labels(
        "llm_service", method, path, error_type
      ).inc()

      logger.error(
        "Request error",
        extra={
          "metric_type": "request_error",
          "method": method,
          "path": path,
          "error_type": error_type,
          "error_message": str(e)
        }
      )

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

def track_llm_generate(func: Callable):
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract llm_type
    gen_config = kwargs.get("gen_config")
    if gen_config:
      try:
        if hasattr(gen_config, "dict"):
          genconfig_dict = gen_config.dict()
        else:
          genconfig_dict = gen_config.model_dump()

        llm_type = genconfig_dict.get("llm_type", "unknown")
        prompt = genconfig_dict.get("prompt", "")
        prompt_size = len(prompt)
        PROMPT_SIZE.labels("llm").observe(prompt_size)
      except Exception as e:
        logger.error(f"Error extracting LLM config: {str(e)}")
        llm_type = "unknown"
        prompt_size = 0
    else:
      llm_type = "unknown"
      prompt_size = 0

    # Extract user information if available
    user_data = kwargs.get("user_data", None)
    if user_data and isinstance(user_data, dict):
      user_id = user_data.get("email", "unknown")
      record_user_activity(user_id, "llm_generation")

    request_id, trace = _get_request_context(args)

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      LLM_GENERATE_COUNT.labels(llm_type=llm_type, status="success").inc()

      logger.info(
        "LLM generation successful",
        extra={
          "metric_type": "llm_generation",
          "llm_type": llm_type,
          "status": "success",
          "prompt_size": prompt_size
        }
      )

      return result
    except Exception as e:
      LLM_GENERATE_COUNT.labels(llm_type=llm_type, status="error").inc()

      logger.error(
        "LLM generation failed",
        extra={
          "metric_type": "llm_generation",
          "llm_type": llm_type,
          "status": "error",
          "prompt_size": prompt_size,
          "error_message": str(e)
        }
      )
      raise
    finally:
      latency = time.time() - start_time
      LLM_GENERATE_LATENCY.labels(llm_type=llm_type).observe(latency)

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
  @wraps(func)
  async def wrapper(*args, **kwargs):
    embedding_config = kwargs.get("embeddings_config")
    if embedding_config:
      try:
        if hasattr(embedding_config, "dict"):
          embedding_config_dict = embedding_config.dict()
        else:
          embedding_config_dict = embedding_config.model_dump()

        embedding_type = embedding_config_dict.get("embedding_type", "unknown")
        text = embedding_config_dict.get("text", "")
        text_size = len(text)
        PROMPT_SIZE.labels("embedding").observe(text_size)
      except Exception as e:
        logger.error(f"Error extracting embedding config: {str(e)}")
        embedding_type = "unknown"
        text_size = 0
    else:
      embedding_type = "unknown"
      text_size = 0

    # Extract user information if available
    user_data = kwargs.get("user_data", None)
    if user_data and isinstance(user_data, dict):
      user_id = user_data.get("email", "unknown")
      record_user_activity(user_id, "embedding_generation")

    request_id, trace = _get_request_context(args)
    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      EMBEDDING_GENERATE_COUNT.labels(embedding_type=embedding_type, status="success").inc()

      logger.info(
        "Embedding generation successful",
        extra={
          "metric_type": "embedding_generation",
          "embedding_type": embedding_type,
          "status": "success",
          "text_size": text_size
        }
      )

      return result
    except Exception as e:
      EMBEDDING_GENERATE_COUNT.labels(embedding_type=embedding_type, status="error").inc()

      logger.error(
        "Embedding generation failed",
        extra={
          "metric_type": "embedding_generation",
          "embedding_type": embedding_type,
          "status": "error",
          "text_size": text_size,
          "error_message": str(e)
        }
      )
      raise
    finally:
      latency = time.time() - start_time

      EMBEDDING_GENERATE_LATENCY.labels(embedding_type=embedding_type).observe(latency)

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
  """Decorator to track chat generation metrics"""
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Extract parameters based on endpoint pattern
    gen_config = kwargs.get("gen_config", None)
    chat_id = kwargs.get("chat_id", None)
    user_id = "unknown"

    llm_type = "unknown"
    with_file = False
    with_tools = False
    prompt_size = 0

    # Get request context
    request_id, trace = _get_request_context(args)

    try:
      # Extract user information
      user_data = kwargs.get("user_data", None)
      if user_data and isinstance(user_data, dict):
        user_id = user_data.get("email", "unknown")
        record_user_activity(user_id, "chat_generation")

      # For create_user_chat function
      if not gen_config:
        prompt = kwargs.get("prompt", "")
        llm_type = kwargs.get("llm_type", "unknown")
        chat_file = kwargs.get("chat_file", None)
        chat_file_url = kwargs.get("chat_file_url", None)
        tool_names = kwargs.get("tool_names", None)

        with_file = (chat_file is not None or chat_file_url is not None)
        with_tools = tool_names is not None
        prompt_size = len(prompt) if prompt else 0

      else:
        if hasattr(gen_config, "dict"):
          genconfig_dict = gen_config.dict()
        else:
          genconfig_dict = gen_config.model_dump()

        llm_type = genconfig_dict.get("llm_type", "unknown")
        prompt = genconfig_dict.get("prompt", "")
        with_file = (genconfig_dict.get("chat_file_b64") is not None or
                    genconfig_dict.get("chat_file_url") is not None)
        with_tools = genconfig_dict.get("tool_names") is not None
        prompt_size = len(prompt)

      if prompt_size > 0:
        PROMPT_SIZE.labels("chat").observe(prompt_size)
    except Exception as e:
      logger.error(
        "Error extracting chat parameters",
        extra={
          "metric_type": "chat_parameters_error",
          "error_message": str(e)
        }
      )

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      CHAT_GENERATE_COUNT.labels(
        llm_type=llm_type,
        with_file=str(with_file),
        with_tools=str(with_tools),
        status="success",
        user_id=user_id
      ).inc()

      log_extra = {
        "metric_type": "chat_generation",
        "llm_type": llm_type,
        "with_file": with_file,
        "with_tools": with_tools,
        "prompt_size": prompt_size,
        "status": "success",
        "user_id": user_id
      }

      if isinstance(result, dict) and "data" in result and "history" in result["data"]:
        history_size = len(result["data"]["history"])
        CHAT_HISTORY_SIZE.labels(llm_type=llm_type).observe(history_size)
        log_extra["history_size"] = history_size

      logger.info("Chat generation successful", extra=log_extra)

      return result
    except Exception as e:
      CHAT_GENERATE_COUNT.labels(
        llm_type=llm_type,
        with_file=str(with_file),
        with_tools=str(with_tools),
        status="error",
        user_id=user_id
      ).inc()

      logger.error(
        "Chat generation failed",
        extra={
          "metric_type": "chat_generation",
          "llm_type": llm_type,
          "with_file": with_file,
          "with_tools": with_tools,
          "prompt_size": prompt_size,
          "status": "error",
          "user_id": user_id,
          "error_message": str(e)
        }
      )
      raise
    finally:
      latency = time.time() - start_time
      CHAT_GENERATE_LATENCY.labels(
        llm_type=llm_type,
        with_file=str(with_file),
        with_tools=str(with_tools)
      ).observe(latency)

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
  @wraps(func)
  async def async_wrapper(*args, **kwargs):
    user_data = kwargs.get("user_data", None)
    user_id = user_data.get("email", "unknown") if user_data else "unknown"

    request_id, trace = _get_request_context(args)

    try:
      result = await func(*args, **kwargs)

      func_name = func.__name__
      if "create" in func_name and isinstance(result, dict) and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).inc()
        record_user_activity(user_id, "chat_create")

        logger.info(
          "Chat created",
          extra={
            "metric_type": "chat_operation",
            "operation": "create",
            "user_id": user_id
          }
        )

      if "delete" in func_name and isinstance(result, dict) and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).dec()
        record_user_activity(user_id, "chat_delete")

        logger.info(
          "Chat deleted",
          extra={
            "metric_type": "chat_operation",
            "operation": "delete",
            "user_id": user_id
          }
        )

      return result
    except Exception as e:
      logger.error(
        "Chat operation failed",
        extra={
          "metric_type": "chat_operation",
          "operation": func.__name__,
          "user_id": user_id,
          "error_message": str(e)
        }
      )
      raise

  @wraps(func)
  def sync_wrapper(*args, **kwargs):
    user_data = kwargs.get("user_data", None)
    user_id = user_data.get("email", "unknown") if user_data else "unknown"

    request_id, trace = _get_request_context(args)

    try:
      result = func(*args, **kwargs)

      func_name = func.__name__
      if "create" in func_name and isinstance(result, dict) and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).inc()
        record_user_activity(user_id, "chat_create")

        logger.info(
          "Chat created",
          extra={
            "metric_type": "chat_operation",
            "operation": "create",
            "user_id": user_id
          }
        )

      if "delete" in func_name and isinstance(result, dict) and result.get("success"):
        ACTIVE_CHATS_TOTAL.labels(user_id=user_id).dec()
        record_user_activity(user_id, "chat_delete")

        logger.info(
          "Chat deleted",
          extra={
            "metric_type": "chat_operation",
            "operation": "delete",
            "user_id": user_id
          }
        )

      return result
    except Exception as e:
      logger.error(
        "Chat operation failed",
        extra={
          "metric_type": "chat_operation",
          "operation": func.__name__,
          "user_id": user_id,
          "error_message": str(e)
        }
      )
      raise

  if asyncio.iscoroutinefunction(func):
    return async_wrapper
  else:
    return sync_wrapper

def track_agent_execution(func: Callable):
  @wraps(func)
  async def wrapper(*args, **kwargs):
    agent_type = kwargs.get("agent_type", "unknown")
    agent_name = kwargs.get("agent_name", "unknown")

    # Extract user information if available
    user_data = kwargs.get("user_data", None)
    if user_data and isinstance(user_data, dict):
      user_id = user_data.get("email", "unknown")
      record_user_activity(user_id, "agent_execution")

    request_id, trace = _get_request_context(args)

    start_time = time.time()
    try:
      # Call the original function
      result = await func(*args, **kwargs)

      AGENT_EXECUTION_COUNT.labels(agent_type=agent_type, status="success").inc()

      logger.info(
        "Agent execution successful",
        extra={
          "metric_type": "agent_execution",
          "agent_type": agent_type,
          "agent_name": agent_name,
          "status": "success"
        }
      )

      return result
    except Exception as e:
      AGENT_EXECUTION_COUNT.labels(agent_type=agent_type, status="error").inc()

      logger.error(
        "Agent execution failed",
        extra={
          "metric_type": "agent_execution",
          "agent_type": agent_type,
          "agent_name": agent_name,
          "status": "error",
          "error_message": str(e)
        }
      )
      raise
    finally:
      latency = time.time() - start_time
      AGENT_EXECUTION_LATENCY.labels(agent_type=agent_type).observe(latency)

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
    # Extract vector DB type and engine name
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
    except Exception as e:
      logger.error(f"Error extracting vector DB info: {str(e)}")

    # Extract user information if available
    user_data = kwargs.get("user_data", None)
    if user_data and isinstance(user_data, dict):
      user_id = user_data.get("email", "unknown")
      record_user_activity(user_id, "vector_db_query")

    request_id, trace = _get_request_context(args)

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      VECTOR_DB_QUERY_COUNT.labels(db_type=db_type, engine_name=engine_name, status="success").inc()

      logger.info(
        "Vector DB query successful",
        extra={
          "metric_type": "vector_db_query",
          "db_type": db_type,
          "engine_name": engine_name,
          "status": "success"
        }
      )

      return result
    except Exception as e:
      VECTOR_DB_QUERY_COUNT.labels(db_type=db_type, engine_name=engine_name, status="error").inc()

      logger.error(
        "Vector DB query failed",
        extra={
          "metric_type": "vector_db_query",
          "db_type": db_type,
          "engine_name": engine_name,
          "status": "error",
          "error_message": str(e)
        }
      )
      raise
    finally:
      latency = time.time() - start_time
      VECTOR_DB_QUERY_LATENCY.labels(db_type=db_type, engine_name=engine_name).observe(latency)

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
    # Extract vector DB type and engine name from config
    gen_config = kwargs.get("gen_config")
    db_type = "unknown"
    engine_name = "unknown"

    if gen_config:
      try:
        if hasattr(gen_config, "dict"):
          genconfig_dict = gen_config.dict()
        else:
          genconfig_dict = gen_config.model_dump()

        db_type = genconfig_dict.get("vector_store", "unknown")
        engine_name = genconfig_dict.get("query_engine", "unknown")
      except Exception as e:
        logger.error(f"Error extracting vector DB build config: {str(e)}")

    # Extract user information if available
    user_data = kwargs.get("user_data", None)
    if user_data and isinstance(user_data, dict):
      user_id = user_data.get("email", "unknown")
      record_user_activity(user_id, "vector_db_build")

    request_id, trace = _get_request_context(args)

    start_time = time.time()
    try:
      result = await func(*args, **kwargs)

      VECTOR_DB_BUILD_COUNT.labels(db_type=db_type, engine_name=engine_name, status="success").inc()

      logger.info(
        "Vector DB build initiated",
        extra={
          "metric_type": "vector_db_build",
          "db_type": db_type,
          "engine_name": engine_name,
          "status": "success"
        }
      )

      return result
    except Exception as e:
      VECTOR_DB_BUILD_COUNT.labels(db_type=db_type, engine_name=engine_name, status="error").inc()

      logger.error(
        "Vector DB build failed",
        extra={
          "metric_type": "vector_db_build",
          "db_type": db_type,
          "engine_name": engine_name,
          "status": "error",
          "error_message": str(e)
        }
      )
      raise
    finally:
      latency = time.time() - start_time
      VECTOR_DB_BUILD_LATENCY.labels(db_type=db_type, engine_name=engine_name).observe(latency)

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
