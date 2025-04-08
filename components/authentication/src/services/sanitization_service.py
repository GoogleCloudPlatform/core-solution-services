# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility methods for sanitizing token and user data for logging."""

def sanitize_token_data(token_data):
  """Sanitizes token data for logging to remove sensitive/excessive information.
  
  Args:
      token_data: The token data dictionary to sanitize
      
  Returns:
      dict: Sanitized token data safe for logging
  """
  if not token_data or not isinstance(token_data, dict):
    return token_data

  # Create a copy to avoid modifying the original
  sanitized = token_data.copy()

  # Remove or mask sensitive fields
  if "picture" in sanitized:
    sanitized["picture"] = "[REDACTED]"

  # Truncate excessively long fields
  if "iss" in sanitized and isinstance(
    sanitized["iss"], str) and len(sanitized["iss"]) > 30:
    sanitized["iss"] = sanitized["iss"][:30] + "..."

  # Remove unnecessary fields
  fields_to_remove = [
    "firebase",   # Contains overly identity information
    "auth_time",  # Not typically needed in logs
    "iat",        # Internal timestamp
    "exp"         # Internal timestamp
  ]

  for field in fields_to_remove:
    if field in sanitized:
      del sanitized[field]

  return sanitized


def sanitize_user_data(user_dict):
  """Sanitizes user data for logging to handle date objects
    and remove sensitive information.
  
  Args:
      user_dict: User dictionary to sanitize
      
  Returns:
      dict: Sanitized user data safe for logging
  """
  if not user_dict or not isinstance(user_dict, dict):
    return user_dict

  # Create a copy to avoid modifying the original
  sanitized = {}

  # Include only necessary fields with proper formatting
  include_fields = [
    "user_id", "email", "user_type", "status", 
    "access_api_docs", "id", "key"
  ]

  for field in include_fields:
    if field in user_dict:
      sanitized[field] = user_dict[field]

  # Handle datetime fields properly
  datetime_fields = ["created_time", "last_modified_time"]
  for field in datetime_fields:
    if field in user_dict and user_dict[field] is not None:
      try:
        # Convert to ISO format string if it has an isoformat method
        if hasattr(user_dict[field], "isoformat"):
          sanitized[field] = user_dict[field].isoformat()
        else:
          sanitized[field] = str(user_dict[field])
      except (AttributeError, TypeError) as e:
        # Handle attribute or type errors specifically
        sanitized[field] = f"[Error formatting datetime: {str(e)}]"
      except ValueError as e:
        # Handle value errors (invalid datetime values)
        sanitized[field] = f"[Invalid datetime: {str(e)}]"

  return sanitized
