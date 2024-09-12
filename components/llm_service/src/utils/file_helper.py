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
File processing helper functions.
"""
# pylint: disable=broad-exception-caught

import os.path
from base64 import b64decode

def validate_multimodal_vision_file_type(file_name, file_b64):
  # Validate the file type and ensure that it is either a text or image
  # and is compatible with multimodal LLMs. Returns the file extension if valid

  vertex_mime_types = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".mp4": "video/mp4",
    ".mov": "video/mov",
    ".avi": "video/avi",
    ".mpeg": "video/mpeg",
    ".mpg": "video/mpg",
    ".wmv": "video/wmv"
  }
  file_extension = os.path.splitext(file_name)[1]
  file_extension = vertex_mime_types.get(file_extension)
  if not file_extension:
    return False

  # Make sure that the user file b64 is a valid image or video
  image_signatures = {
      b"\x89\x50\x4E\x47\x0D\x0A\x1A\x0A": "png",
      b"\xFF\xD8\xFF": "jpg",
      b"\xFF\xD8": "jpeg",
      b"\x47\x49\x46\x38": "gif",
      b"\x00\x00\x00 ftyp": "mp4",
      b"\x00\x00\x00\x14": "mov",
      b"RIFF": "avi",
      b"\x00\x00\x01\xba!\x00\x01\x00": "mpeg",
      b"\x00\x00\x01\xB3": "mpg",
      b"0&\xb2u\x8ef\xcf\x11": "wmv"
  }
  file_header = b64decode(file_b64)[:8]  # Get the first 8 bytes
  user_file_type = None
  for sig, file_format in image_signatures.items():
    if file_header.startswith(sig):
      user_file_type = file_format
      break

  if not user_file_type:
    return False

  return [True, file_extension]
