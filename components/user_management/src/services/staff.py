# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Service file for Staff"""
from common.models import Staff
from common.utils.errors import ConflictError


def create_staff(input_staff):
  """Method to create a Staff"""
  existing_staff = Staff.find_by_email(input_staff.email)
  if existing_staff is not None:
    raise ConflictError(
      f"Staff with the given email: {input_staff.email} already exists")
  staff_dict = {**input_staff.dict()}
  staff = Staff()
  staff = staff.from_dict(staff_dict)
  staff.uuid = ""
  staff.save()
  staff.uuid = staff.id
  staff.update()
  staff = staff.get_fields(reformat_datetime=True)
  return staff

def update_staff(uuid, input_staff):
  """Method to update Staff"""
  existing_staff = Staff.find_by_uuid(uuid)
  input_staff_dict = {**input_staff.dict(exclude_unset=True)}
  staff_fields = existing_staff.get_fields()
  for key, value in input_staff_dict.items():
    if value is not None:
      staff_fields[key] = value
  for key, value in staff_fields.items():
    setattr(existing_staff, key, value)
  existing_staff.update()
  staff_fields = existing_staff.get_fields(reformat_datetime=True)
  return staff_fields
