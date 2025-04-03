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

"""Common monitoring utilities for request tracking and metrics across services."""

# Import and expose the key middleware components for easy access
from common.monitoring.middleware import (
  RequestTrackingMiddleware,
  PrometheusMiddleware,
  create_metrics_router,
  get_request_context
)

# Import and expose common metrics utilities
from common.monitoring.metrics import (
  operation_tracker,
  extract_user_id,
  log_operation_result
)

__all__ = [
  # Middleware components
  'RequestTrackingMiddleware',
  'PrometheusMiddleware',
  'create_metrics_router',
  'get_request_context',

  # Metrics utilities
  'operation_tracker',
  'extract_user_id',
  'log_operation_result'
]
