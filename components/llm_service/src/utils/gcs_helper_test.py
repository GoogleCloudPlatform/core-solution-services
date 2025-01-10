# Copyright 2024 Google LLC
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
  Unit tests for LLM Service gcs helper utils
"""
from utils.gcs_helper import create_bucket_for_file

def test_create_bucket_long_filename():
  """This test was added because there was previously an error
  where the algorithm for creating a bucket to store a file provided in chat
  would break if a file with a name over 64 characters was provided twice"""
  create_bucket_for_file(("incredibly long file name that goes "
    "well over the limit for a google storage bucket.pdf"))
  create_bucket_for_file(("incredibly long file name that goes "
    "well over the limit for a google storage bucket.pdf"))
