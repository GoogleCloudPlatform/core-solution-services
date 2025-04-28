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

"""

This module provides context variables for tracking request information across
async boundaries.

"""

import contextvars
import logging
from typing import Dict, List, Optional, Tuple

# Create context variables
request_id_var = contextvars.ContextVar("request_id", default="-")
trace_var = contextvars.ContextVar("trace", default="-")
session_id_var = contextvars.ContextVar("session_id", default="-")
cloud_trace_context_var = contextvars.ContextVar("cloud_trace_context", default="-")

# Logger for this module
logger = logging.getLogger(__name__)

def debug_context_vars() -> Dict[str, str]:
  """Print and return the current values of all context variables."""
  context = {
    "request_id": request_id_var.get(),
    "trace": trace_var.get(),
    "session_id": session_id_var.get(),
    "cloud_trace_context": cloud_trace_context_var.get()
  }
  logger.debug(f"Current context vars: {context}")
  return context

def get_context() -> Dict[str, str]:
  """Get all context variables as a dictionary."""
  return {
    "request_id": request_id_var.get(),
    "trace": trace_var.get(),
    "session_id": session_id_var.get(),
    "cloud_trace_context": cloud_trace_context_var.get()
  }

def get_trace_headers() -> Dict[str, str]:
  """
  Get trace headers from context variables for propagation.
  
  Returns:
    dict: Headers with trace context information
  """
  context = get_context()
  headers = {}
  
  # Add request ID if available
  request_id = context.get("request_id")
  if request_id and request_id != "-":
    headers["X-Request-ID"] = request_id
  
  # Add session ID if available
  session_id = context.get("session_id") 
  if session_id and session_id != "-":
    headers["X-Session-ID"] = session_id
  
  # Add cloud trace context if available
  cloud_trace_context = context.get("cloud_trace_context")
  if cloud_trace_context and cloud_trace_context != "-":
    headers["X-Cloud-Trace-Context"] = cloud_trace_context
  
  return headers

def set_context(
  request_id: Optional[str] = None,
  trace: Optional[str] = None,
  session_id: Optional[str] = None,
  cloud_trace_context: Optional[str] = None
) -> List[Tuple[contextvars.ContextVar, contextvars.Token]]:
  """Set context variables and return tokens for resetting.
  
  Args:
    request_id: Request ID to set
    trace: Trace ID to set
    session_id: Session ID to set
    cloud_trace_context: Raw Cloud Trace Context to set
    
  Returns:
    List of (var, token) pairs that can be used to reset context
  """
  tokens = []

  if request_id is not None:
    token = request_id_var.set(request_id)
    tokens.append((request_id_var, token))

  if trace is not None:
    token = trace_var.set(trace)
    tokens.append((trace_var, token))

  if session_id is not None:
    token = session_id_var.set(session_id)
    tokens.append((session_id_var, token))
    
  if cloud_trace_context is not None:
    token = cloud_trace_context_var.set(cloud_trace_context)
    tokens.append((cloud_trace_context_var, token))

  return tokens

def reset_context(
  tokens: List[Tuple[contextvars.ContextVar, contextvars.Token]]
) -> None:
  """Reset context variables using the tokens from set_context.
  
  Args:
    tokens: List of (var, token) pairs from set_context
  """
  for var, token in tokens:
    var.reset(token)

class AsyncContextPreserver:
  """Context manager to preserve context vars across async boundaries.
  
  Usage:
    async def some_async_function():
      with AsyncContextPreserver() as context:
        # Do work, await things, etc.
        await some_other_async_function()
              
      # Now context variables are restored to what they were
  """

  def __init__(self):
    self.tokens = None
    self.preserved_context = None

  def __enter__(self):
    # Save current context
    self.preserved_context = get_context()
    return self.preserved_context

  def __exit__(self, exc_type, exc_val, exc_tb):
    # Restore context
    if self.preserved_context:
      _ = set_context(
        request_id=self.preserved_context.get("request_id"),
        trace=self.preserved_context.get("trace"),
        session_id=self.preserved_context.get("session_id"),
        cloud_trace_context=self.preserved_context.get("cloud_trace_context")
      )
      # We don't need to keep the tokens because we're restoring
      # not resetting
