"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""Function to generate tokens"""
import jwt

class TokenGenerator:
  """Class to handle token generator functions"""

  @classmethod
  def generate_jwt_token(cls, payload, headers, secret) -> str:
    """Generates a JWT token with provided payload, headers and secret"""
    jwt_token = jwt.encode(payload, secret, headers=headers)
    return jwt_token
