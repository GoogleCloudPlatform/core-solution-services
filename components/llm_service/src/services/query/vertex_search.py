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
from typing import List
from google.api_core.client_options import ClientOptions
#from google.cloud import discoveryengine_v1 as discoveryengine
from google.cloud import discoveryengine
from config import PROJECT_ID
from common.models import QueryEngine, QueryReference
from common.utils.logging_handler import Logger

Logger = Logger.get_logger(__file__)

def query_vertex_search(q_engine: QueryEngine,
                        search_query: str) -> List[QueryReference]:
  """
  For a query prompt, retrieve text chunks with doc references
  from matching documents from a vertex search engine.

  Args:
    q_engine: QueryEngine to search
    search_query (str):  user query

  Returns:
    list of QueryReference models

  """
  data_store_id = q_engine.name

  # get search results from vertex
  search_responses = vertex_search(data_store_id, search_query)

  # create query reference models to store results
  query_references = []
  for search_response in search_responses:
    for search_result in search_response.results:
      content = search_result.document.content
      query_reference = QueryReference(
        query_engine_id=q_engine.id,
        query_engine=q_engine.name,
        chunk_text=content
      )
      query_reference.save()
      query_references.append(query_reference)
  return query_references

def vertex_search(data_store_id: str,
                  search_query: str
                  ) -> List[discoveryengine.SearchResponse]:
  """ Send a search request to Vertex Search """
  project_id = PROJECT_ID
  location = "global"

  #  For more information, refer to:
  # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
  client_options = (
      ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
      if location != "global"
      else None
  )

  # Create a client
  client = discoveryengine.SearchServiceClient(client_options=client_options)

  # The full resource name of the search engine serving config
  # e.g. projects/{project_id}/locations/{location}/dataStores/{data_store_id}/servingConfigs/{serving_config_id}
  serving_config = client.serving_config_path(
      project=project_id,
      location=location,
      data_store=data_store_id,
      serving_config="default_config",
  )

  # Optional: Configuration options for search
  # Refer to the `ContentSearchSpec` reference for all supported fields:
  # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest.ContentSearchSpec
  content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
      # For information about snippets, refer to:
      # https://cloud.google.com/generative-ai-app-builder/docs/snippets
      snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
          return_snippet=True
      ),
      # For information about search summaries, refer to:
      # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
      summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
          summary_result_count=5,
          include_citations=True,
          ignore_adversarial_query=True,
          ignore_non_summary_seeking_query=True,
      ),
  )

  # Refer to the `SearchRequest` reference for all supported fields:
  # https://cloud.google.com/python/docs/reference/discoveryengine/latest/google.cloud.discoveryengine_v1.types.SearchRequest
  request = discoveryengine.SearchRequest(
      serving_config=serving_config,
      query=search_query,
      page_size=10,
      content_search_spec=content_search_spec,
      query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
          condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
      ),
      spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
          mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
      ),
  )

  response = client.search(request)

  return response


def build_vertex_search(q_engine: QueryEngine):
  """
  Build a Vertex Search-based Query Engine
  
  q_engine.doc_url must specify either a gcs uri,
     or bq://<bigquery dataset and table separated by colons>
  ie.
  q_engine.doc_url = "gs://bucket/optional_subfolder"
    or
  q_engine.doc_url = "bq://BIGQUERY_DATASET:BIGQUERY_TABLE"
  """

  data_url = q_engine.doc_url
  project_id = PROJECT_ID
  location = "global"
  data_store_id = q_engine.name

  # create vertex search client
  client, parent = create_client(project_id, location, data_store_id)

  # create operation to import data
  operation = None
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
