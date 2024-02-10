# Copyright 2024 Google LLC
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
Vertex Search-based Query Engines
"""
# pylint: disable=line-too-long

from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine
from config import PROJECT_ID
from common.models import QueryEngine
from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)

def query_vertex_search():
  pass

# Must specify either `gcs_uri` or (`bigquery_dataset` and `bigquery_table`)
# Format: `gs://bucket/directory/object.json` or `gs://bucket/directory/*.json`
# gcs_uri = "YOUR_GCS_PATH"
# bigquery_dataset = "YOUR_BIGQUERY_DATASET"
# bigquery_table = "YOUR_BIGQUERY_TABLE"


def build_vertex_search(q_engine: QueryEngine):

  data_url = q_engine.doc_url
  project_id = PROJECT_ID
  location = "global"
  data_store_id = q_engine.name

  # create vertex search client
  client, parent = create_client(project_id, location, data_store_id)

  # create operation to import data
  if data_url.startswith("gs://"):
    operation = import_documents_gcs(data_url, client, parent)

  elif data_url.startswith("bq://"):
    bq_datasource = data_url.split("bq://")[1].split("/")[0]
    bigquery_dataset = bq_datasource.split(":")[0]
    bigquery_table = bq_datasource.split(":")[1]

    operation = import_documents_bq(project_id, bigquery_dataset, bigquery_table, client, parent)

  Logger.info(f"Waiting for operation to complete: {operation.operation.name}")
  response = operation.result()

  # Once the operation is complete,
  # get information from operation metadata
  metadata = discoveryengine.ImportDocumentsMetadata(operation.metadata)

  # save metadata in query engine
  q_engine.vertex_metadata = metadata
  q_engine.save()

  # Handle the response
  print(response)
  print(metadata)

  return operation.operation.name



def create_client(project_id: str,
                  location: str,
                  data_store_id: str):
  #  For more information, refer to:
  # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
  client_options = (
      ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
      if location != "global"
      else None
  )

  # Create a client
  client = discoveryengine.DocumentServiceClient(client_options=client_options)

  # The full resource name of the search engine branch.
  # e.g. projects/{project}/locations/{location}/dataStores/{data_store_id}/branches/{branch}
  parent = client.branch_path(
      project=project_id,
      location=location,
      data_store=data_store_id,
      branch="default_branch",
  )
  return client, parent


def import_documents_gcs(gcs_uri: str,
                         client, parent) -> str:

  request = discoveryengine.ImportDocumentsRequest(
      parent=parent,
      gcs_source=discoveryengine.GcsSource(
          input_uris=[gcs_uri], data_schema="custom"
      ),
      # Options: `FULL`, `INCREMENTAL`
      reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
  )

  # Make the request
  operation = client.import_documents(request=request)

  return operation

def import_documents_bq(project_id: str,
                        bigquery_dataset: str,
                        bigquery_table: str,
                        client, parent) -> str:

  request = discoveryengine.ImportDocumentsRequest(
      parent=parent,
      bigquery_source=discoveryengine.BigQuerySource(
          project_id=project_id,
          dataset_id=bigquery_dataset,
          table_id=bigquery_table,
          data_schema="custom",
      ),
      # Options: `FULL`, `INCREMENTAL`
      reconciliation_mode=discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
  )

  # Make the request
  operation = client.import_documents(request=request)

  return operation
