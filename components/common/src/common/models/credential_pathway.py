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

"""Credential and Pathway Service Data Models"""

from fireo.fields import TextField
from common.models import NodeItem, BaseModel
from common.utils.errors import ResourceNotFoundException


class Credential(NodeItem):
  """Credential Class"""
  # schema for object
  uuid = TextField(required=True)

  class Meta:
    collection_name = BaseModel.DATABASE_PREFIX + "credentials"
    ignore_none_field = False

  @classmethod
  def find_by_uuid(cls, uuid):
    credential = Credential.collection.filter("uuid", "==", uuid).get()
    if credential is None:
      raise ResourceNotFoundException(f"Credential with uuid {uuid} not found")
    return credential


class LearningPathway(NodeItem):
  """Learning Pathway Class"""
  # schema for object
  uuid = TextField(required=True)
  title = TextField(required=True)

  class Meta:
    collection_name = BaseModel.DATABASE_PREFIX + "learning_pathways"
    ignore_none_field = False

  @classmethod
  def find_by_uuid(cls, uuid):
    learning_pathways = LearningPathway.collection.filter("uuid", "==",
                                                          uuid).get()
    if learning_pathways is None:
      raise ResourceNotFoundException(
          f"Learning Pathway with uuid {uuid} not found")
    return learning_pathways
