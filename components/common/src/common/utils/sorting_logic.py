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
    ----------------------------------------------------------------
    Args:
      collection_manager: Firestore Collection Manager
      sort_by: Sort By Field
      sort_order: Sort Order
      skip: Skip Count
      limit: Limit Count
    Returns:
      Collection Manager: Firestore Collection
  """

  return collection_manager.order(f"{sort_by}").offset(
    skip).fetch(limit) if sort_order == "ascending" else \
    collection_manager.order(f"-{sort_by}").offset(skip).fetch(limit)


def get_sorted_list(sort_by, sort_order, collection_manager) -> list:
  """
    Generic Function for Sorting Logic through pythonic way
    ----------------------------------------------------------------
    Args:
      collection_manager: Firestore Collection Manager
      sort_by: Sort By Field
      sort_order: Sort Order
    Returns:
      Collection Manager: list of firestore records in dictionary
  """
  reverse = sort_order == "descending"

  collection_contents = collection_manager.fetch()
  collection_contents = [i.get_fields(reformat_datetime=True) for i in
                         collection_contents if hasattr(i, sort_by)]
  return sorted(collection_contents, key=lambda document: document.get(
    sort_by), reverse=reverse)


def sort_records(sort_by: str, sort_order: str, records: list,
                key: str) -> list:
  """
    Generic Function for Sorting records through pythonic way
    ----------------------------------------------------------------------------
    Args:
      records: Collection Records
      key: Sort Key
      sort_by: Sort By Field
      sort_order: Sort Order
    Returns:
      List: list of firestore records in dictionary
  """
  reverse = sort_order == "descending"
  return sorted(records, key=lambda k: k[key][sort_by], reverse=reverse)
