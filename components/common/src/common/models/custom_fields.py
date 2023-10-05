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

"""Custom Fields for Fireo"""
from fireo.fields import Field
import os
# pylint: disable=broad-exception-raised

GCS_BUCKET = os.environ.get("PROJECT_ID")

class GCSPathField(Field):
  """Custom field to save only GCS file path to firestore and
    return full URI when retrieved"""

  def db_value(self, val):
    """Storing modfied val to DB"""
    if val:
      try:
        blob_name = "/".join(val.split("gs://")[1].split("/")[1:])
        return blob_name
      except Exception as e:
        raise Exception("Invalid GCS URI: " + str(val)) from e
    return val

  def field_value(self, val):
    """Returning complete path"""
    if val and val.startswith("gs://"):
      return val
    elif val:
      return "gs://" + GCS_BUCKET + "/" + val
    return val
