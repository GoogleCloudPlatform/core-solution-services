"""
  Script to create indexing in firestore for dev environment
"""

import os
import json
import sys
from google.cloud import firestore_admin_v1
import firebase_admin
from firebase_admin import firestore

PROJECT_ID = os.getenv("PROJECT_ID", "your-project-id")

client = firestore_admin_v1.FirestoreAdminClient()
app = firebase_admin.initialize_app()
db = firestore.client()

# disabling for linting to pass
# pylint: disable = broad-exception-raised, broad-except

def create_index(index_data):
  """Create index in the firestore"""
  collection_group = index_data.get("collection_group")
  project = (f"projects/{PROJECT_ID}/databases/(default)/"
      f"collectionGroups/{collection_group}")
  del index_data["collection_group"]
  request = firestore_admin_v1.CreateIndexRequest(
      parent=project, index=index_data)

  try:
    client.create_index(request=request)
    print(f"created index for {collection_group}")
  except Exception as e:
    print(f"Exception while creating index for {collection_group}", e)
    if type(e).__name__ != "AlreadyExists":
      sys.exit(1)

def create_dummy_collection(collection_name):
  data = {"name": "Dummy"}
  db.collection(collection_name).document(f"{collection_name}_dummy").set(data)

def delete_dummy_collection(collection_name):
  db.collection(collection_name).document(f"{collection_name}_dummy").delete()

def process_indexes_file(index_file_name):
  indexes = []

  with open(index_file_name, encoding="utf-8") as indexes_file:
    service_index_mapping = json.load(indexes_file)
    for _, index_list in service_index_mapping.items():
      indexes.extend(index_list)

  collection_groups = {i["collection_group"] for i in indexes}
  for collection_group in collection_groups:
    print(f"CollectionGroup = {collection_group}")
    create_dummy_collection(collection_group)

  for index in indexes:
    create_index(index)

  for collection_group in collection_groups:
    delete_dummy_collection(collection_group)


if __name__ == "__main__":
  if PROJECT_ID is None:
    raise Exception("PROJECT_ID is not defined. Indexing skipped.")

  index_files = [
        "index_llms.json"
  ]
  for file_name in index_files:
    process_indexes_file(file_name)
