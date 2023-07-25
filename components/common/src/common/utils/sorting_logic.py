"""
Copyright 2023 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

"""
Generic function for Sorting is implemented
"""


def collection_sorting(collection_manager: any, sort_by: str,
                       sort_order: str, skip: int, limit: int) -> any:
  """
  Generic Function for Firestore Collection Sorting Logic
  :collection_manager: Object
  :sort_by: string
  :sort_order: const(ascending, descending)
  :return: Firestore Object
  """

  return collection_manager.order(f"{sort_by}").offset(
    skip).fetch(limit) if sort_order == "ascending" else \
    collection_manager.order(f"-{sort_by}").offset(skip).fetch(limit)
