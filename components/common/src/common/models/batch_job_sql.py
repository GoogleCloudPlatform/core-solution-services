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
from peewee import (UUIDField,
                    DateTimeField,
                    TextField,
                    IntegerField,
                    BooleanField,
                    TimestampField)
from playhouse.postgres_ext import ArrayField
from common.models.base_model_sql import SQLBaseModel


class BatchJobModel(SQLBaseModel):
  """Model class for batch job"""
  id = UUIDField()
  name = TextField(required=True, default="")
  input_data = TextField()
  type = TextField(required=True)
  status = TextField(required=True)
  message = TextField(required=True, default="")
  generated_item_id = TextField()
  output_gcs_path = TextField()
  errors = ArrayField(default=[])
  job_logs = ArrayField(default=[])
  metadata = ArrayField(default=[])
  result_data = ArrayField(default=[])
  uuid = TextField()

  @classmethod
  def find_by_name(cls, name):
    pass

  @classmethod
  def find_by_uuid(cls, name):
    pass
    
  @classmethod
  def find_by_job_type(cls, job_type):
    pass
