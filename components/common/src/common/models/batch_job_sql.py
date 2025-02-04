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
import uuid
from peewee import TextField, DoesNotExist
from playhouse.postgres_ext import JSONField
from common.models.base_model_sql import SQLBaseModel


class BatchJobModel(SQLBaseModel):
  """Model class for batch job"""
  name = TextField()
  input_data = TextField(null=True)
  type = TextField()
  status = TextField()
  message = TextField(default="")
  generated_item_id = TextField(null=True)
  output_gcs_path = TextField(null=True)
  errors = JSONField(default=dict)
  job_logs = JSONField(default=dict)
  metadata = JSONField(default=dict)
  result_data = JSONField(default=dict)
  uuid = TextField(primary_key=True, default=str(uuid.uuid4))

  class Meta:
    table_name = SQLBaseModel.DATABASE_PREFIX + "batch_jobs"
    primary_key = False

  @classmethod
  def find_by_name(cls, name):
    """
    Find a batch job by name.
    """
    try:
      return cls.get(cls.name == name)
    except DoesNotExist:
      return None

  @classmethod
  def find_by_uuid(cls, uuid):
    """
    Find a batch job by UUID.
    """
    try:
      return cls.get(cls.uuid == uuid)
    except DoesNotExist:
      return None

  @classmethod
  def find_by_job_type(cls, job_type):
    """
    Find batch jobs by job type.
    """
    return list(cls.select().where(cls.type == job_type))
