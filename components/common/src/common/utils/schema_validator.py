# Copyright 2023 Google LLC
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

"class for checking empty string and spaces"
from pydantic import BaseModel

class BaseConfigModel(BaseModel):
  """Base class for pydantic schema models where str validation required"""

  class Config:
    anystr_strip_whitespace = True
    min_anystr_length =1
    error_msg_templates = {
            "value_error.any_str.min_length":
              "String length must be at least {limit_value}",
            "validation_failed": "String is empty or has only spaces"
        }
