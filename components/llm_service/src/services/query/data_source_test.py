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
"""
  Unit tests for Data Source
"""
import services
import tempfile

import services.query.data_source

def test_get_file_hash():
  correct_hash = (
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
  with tempfile.NamedTemporaryFile() as f:
    f.write(b"hello world!")
    file_hash = services.query.data_source.get_file_hash(f.name)
    assert file_hash == correct_hash
