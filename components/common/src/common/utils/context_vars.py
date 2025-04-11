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

"""Centralized context variables for request tracking and correlation.

This module provides the single source of truth for context variables used
throughout the application. All components should import from this module
rather than creating their own context variables.
"""

import contextvars
import asyncio
from typing import Dict, Any, Optional, Callable, Awaitable
from functools import wraps

# Define context variables in one place to avoid multiple instances
request_id_var = contextvars.ContextVar("request_id", default="-")
trace_var = contextvars.ContextVar("trace", default="-")
session_id_var = contextvars.ContextVar("session_id", default="-")

# Print startup information to help with debugging
print(f"*** STARTUP: context_vars.py initialized context variables ***")
print(f"*** STARTUP: request_id_var ID: {id(request_id_var)} ***")
print(f"*** STARTUP: trace_var ID: {id(trace_var)} ***")
print(f"*** STARTUP: session_id_var ID: {id(session_id_var)} ***")

def get_context() -> Dict[str, str]:
  """Get the current context as a dictionary.
  
  Returns:
    Dict containing request_id, trace, and session_id
  """
  return {
    "request_id": request_id_var.get(),
    "trace": trace_var.get(),
    "session_id": session_id_var.get()
  }

def set_context(
    request_id: Optional[str] = None, 
    trace: Optional[str] = None, 
    session_id: Optional[str] = None) -> Dict[str, contextvars.Token]:
  """Set the context variables and return tokens for resetting.
  
  Args:
    request_id: Optional request ID
    trace: Optional trace ID
    session_id: Optional session ID
    
  Returns:
    Dictionary of tokens that can be used to reset the context
  """
  tokens = {}
  if request_id is not None:
    tokens["request_id"] = request_id_var.set(request_id)
  if trace is not None:
    tokens["trace"] = trace_var.set(trace)
  if session_id is not None:
    tokens["session_id"] = session_id_var.set(session_id)
  return tokens

def reset_context(tokens: Dict[str, contextvars.Token]) -> None:
  """Reset context variables using the provided tokens.
  
  Args:
    tokens: Dictionary of tokens returned by set_context
  """
  if "request_id" in tokens:
    request_id_var.reset(tokens["request_id"])
  if "trace" in tokens:
    trace_var.reset(tokens["trace"])
  if "session_id" in tokens:
    session_id_var.reset(tokens["session_id"])

async def copy_context_to_task(coro: Awaitable, context: Dict[str, str]) -> Any:
  """Copy the current context to a new task/coroutine.
  
  This function ensures context variables are properly propagated to
  child tasks in async code.
  
  Args:
    coro: The coroutine to run with the copied context
    context: Dictionary containing request_id, trace, and session_id
    
  Returns:
    The result of the coroutine
  """
  # Create a new task with the copied context
  task = asyncio.create_task(coro)
  
  # Set the context in the new task
  if context.get("request_id") and context.get("request_id") != "-":
    request_id_var.set(context["request_id"])
  if context.get("trace") and context.get("trace") != "-":
    trace_var.set(context["trace"])
  if context.get("session_id") and context.get("session_id") != "-":
    session_id_var.set(context["session_id"])
  
  # Wait for the task to complete
  return await task

def preserve_context(func):
  """Decorator that preserves context across async boundaries.
  
  This decorator ensures that the context variables are properly
  propagated to async functions, even when they're called from
  different async contexts.
  
  Args:
    func: The async function to decorate
    
  Returns:
    Decorated function that preserves context
  """
  @wraps(func)
  async def wrapper(*args, **kwargs):
    # Capture current context
    context = get_context()
    
    # Create tokens for the new context
    tokens = set_context(
      request_id=context["request_id"],
      trace=context["trace"],
      session_id=context["session_id"]
    )
    
    try:
      # Run the function with preserved context
      return await func(*args, **kwargs)
    finally:
      # Reset context to previous values
      reset_context(tokens)
  
  return wrapper

def debug_context_vars() -> Dict[str, Any]:
  """Print current context variable values for debugging.
  
  Returns:
    Dictionary with the current context values
  """
  context = {
    "request_id": request_id_var.get(),
    "trace": trace_var.get(),
    "session_id": session_id_var.get(),
    "ids": {
      "request_id_var": id(request_id_var),
      "trace_var": id(trace_var),
      "session_id_var": id(session_id_var)
    }
  }
  
  print(f"DEBUG CONTEXT: Current context variable values:")
  print(f"  request_id_var (id={id(request_id_var)}): {request_id_var.get()}")
  print(f"  trace_var (id={id(trace_var)}): {trace_var.get()}")
  print(f"  session_id_var (id={id(session_id_var)}): {session_id_var.get()}")
  
  return context
