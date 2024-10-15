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
SQL model for batch jobs
"""
from peewee import UUIDField, TextField, DoesNotExist
from playhouse.postgres_ext import ArrayField
from common.models import SQLBaseModel


class BatchJobModel(SQLBaseModel):
  """Model class for batch job"""

  id = UUIDField()
  name = TextField(default="")
  input_data = TextField(null=True)
  type = TextField()
  status = TextField()
  message = TextField(default="")
  generated_item_id = TextField(null=True)
  output_gcs_path = TextField(null=True)
  errors = ArrayField(default=[])
  job_logs = ArrayField(default=[])
  metadata = ArrayField(default=[])
  result_data = ArrayField(default=[])
  uuid = TextField(null=True)

  @classmethod
  def find_by_name(cls, name):
    """
    Find a batch job by its name.
    Args:
        name (str): The name of the batch job.
    Returns:
        BatchJobModel: The batch job object if found, None otherwise.
    """
    try:
      return cls.get(cls.name == name)
    except DoesNotExist:
      return None

  @classmethod
  def find_by_uuid(cls, uuid):
    """
    Find a batch job by its UUID.
    Args:
        uuid (str): The UUID of the batch job.
    Returns:
        BatchJobModel: The batch job object if found, None otherwise.
    """
    try:
      return cls.get(cls.uuid == uuid)
    except DoesNotExist:
      return None

  @classmethod
  def find_by_job_type(cls, job_type):
    """
    Find batch jobs by their type.
    Args:
        job_type (str): The type of the batch jobs.
    Returns:
        List[BatchJobModel]: A list of batch job objects matching the type.
    """
    return list(cls.select().where(cls.type == job_type))