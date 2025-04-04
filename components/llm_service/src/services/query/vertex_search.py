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
# pylint: disable=broad-exception-caught

import re
import tempfile
import traceback
from typing import List, Tuple
from pathlib import Path
from google.cloud import storage
from google.api_core.client_options import ClientOptions
from google.api_core.operation import Operation
from google.cloud import discoveryengine_v1alpha as discoveryengine
from config import PROJECT_ID, DEFAULT_WEB_DEPTH_LIMIT
from common.models import QueryEngine, QueryDocument, QueryReference
from common.utils.logging_handler import Logger
from services.query.data_source import DataSourceFile
from services.query.web_datasource import WebDataSource
import proto

Logger = Logger.get_logger(__file__)

# valid file extensions for Vertex Search
VALID_FILE_EXTENSIONS = [".pdf", ".html", ".csv", ".json"]

# as of 2/2025 Vertex Search only supports text modality
DEFAULT_MODALITY = "text"

async def query_vertex_search(q_engine: QueryEngine,
                              search_query: str,
                              num_results: int,
                              query_filter: dict) -> List[QueryReference]:
  """
  For a query prompt, retrieve text chunks with doc references
  from matching documents from a vertex search engine.

  Args:
    q_engine: QueryEngine to search
    search_query (str):  user query
    query_filter (dict): filter for query
  Returns:
    list of QueryReference models

  """
  # vertex search datastore id is stored in q_engine.index_id
  data_store_id = q_engine.index_id

  # TODO: implement query filters for vertex
  Logger.info(f"query filter: {query_filter}")

  # get search results from vertex
  search_results = await perform_vertex_search(data_store_id,
                                               search_query,
                                               num_results)

  # create query document and reference models to store results
  query_references = []
  n = 0
  for search_result in search_results:
    document_data = \
        proto.Message.to_dict(search_result.document)["derived_struct_data"]

    # Find or create document model
    query_document = QueryDocument.find_by_index_file(
        q_engine.id, document_data["link"])
    if not query_document:
      # By not assuming the document models exist, we can more easily search an
      # existing datastore. The LLM Service just needs the datastore id
      # associated with a query engine model.
      Logger.warning(
          f"Creating document model for {document_data['link']} engine"
          f" {q_engine.name}")
      query_document = QueryDocument(
        query_engine_id=q_engine.id,
        query_engine=q_engine.name,
        doc_url=document_data["link"],
        index_file=document_data["link"]
      )
      query_document.save()

    # create query reference model
    Logger.info(
        f"Creating query ref for search result [{document_data['link']}]")
    query_reference = QueryReference(
      query_engine_id=q_engine.id,
      query_engine=q_engine.name,
      document_id=query_document.id,
      document_url=query_document.doc_url,
      modality=DEFAULT_MODALITY,
      document_text=document_data["snippets"][0]["snippet"],
      chunk_id=str(n) # fake chunk id for ux's that dedup on chunk id
    )
    n += 1
    query_reference.save()
    query_references.append(query_reference)

  return query_references

async def perform_vertex_search(data_store_id: str,
                                search_query: str,
                                num_results: int) -> \
    List[discoveryengine.SearchResponse.SearchResult]:
  """ Send a search request to Vertex Search """
  project_id = PROJECT_ID
  location = "global"

  client_options = (
      ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
      if location != "global"
      else None
  )

  # Create a client
  client = \
      discoveryengine.SearchServiceAsyncClient(client_options=client_options)

  # The full resource name of the search engine serving config, e.g.
  # "projects/{project_id}/locations/{location}/dataStores/{data_store_id}"
  # + "/servingConfigs/{serving_config_id}"
  serving_config = client.serving_config_path(
      project=project_id,
      location=location,
      data_store=data_store_id,
      serving_config="default_config",
  )

  # Configuration options for search
  # Refer to the `ContentSearchSpec` reference for all supported fields
  content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
      snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
          return_snippet=True
      ),
      summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
          summary_result_count=num_results,
          include_citations=True,
          ignore_adversarial_query=True,
          ignore_non_summary_seeking_query=True,
      ),
  )

  # Refer to the `SearchRequest` reference for all supported fields
  request = discoveryengine.SearchRequest(
      serving_config=serving_config,
      query=search_query,
      page_size=10,
      content_search_spec=content_search_spec,
      query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
          condition=\
              discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
      ),
      spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
          mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
      ),
  )

  # perform search with client
  response = await client.search(request)

  # get list of results
  result_list = response.results

  return result_list


def build_vertex_search(q_engine: QueryEngine) -> \
    Tuple[List[QueryDocument], List[str]]:
  """
  Build a Vertex Search-based Query Engine

  q_engine.doc_url must specify either a gcs uri, an http:// https://
     URL, or bq://<bigquery dataset and table separated by colons>
  ie.
  q_engine.doc_url = "gs://bucket/optional_subfolder"
    or
  q_engine.doc_url = "bq://BIGQUERY_DATASET:BIGQUERY_TABLE"
    or
  q_engine.doc_url = "https://example.com/news"

  Args:
    q_engine: QueryEngine to build

  Returns:
    Tuple of list of QueryDocument objects of docs processed,
      list of uris of docs not processed
  """
  # initialize some variables
  data_url = q_engine.doc_url
  project_id = PROJECT_ID
  location = "global"

  Logger.info(f"Building vertex search engine [{q_engine.name}] [{data_url}]")

  # initialize doc tracking lists
  docs_to_be_processed = []
  docs_processed = []
  docs_not_processed = []
  doc_models_processed = []

  # initialize datastore id
  data_store_id = None

  # validate data_url
  if not (data_url.startswith("bq://")
       or data_url.startswith("gs://")
       or data_url.startswith("http://") or data_url.startswith("https://")):
    raise RuntimeError(f"Invalid data url: {data_url}")

  try:
    # inventory the documents to be ingested
    if data_url.startswith("http://") or data_url.startswith("https://"):
      # download web docs and store in a GCS bucket
      gcs_url, docs_to_be_processed = download_web_docs(q_engine, data_url)
      data_url = gcs_url
    elif data_url.startswith("bq://"):
      docs_to_be_processed = [DataSourceFile(src_url=data_url)]
    elif data_url.startswith("gs://"):
      docs_to_be_processed = inventory_gcs_files(data_url)

    # create data store
    data_store_id = datastore_id_from_engine(q_engine)
    operation = create_data_store(q_engine, project_id, data_store_id)
    wait_for_operation(operation)

    # perform import
    docs_processed, docs_not_processed = \
        import_documents_to_datastore(data_url,
                                      docs_to_be_processed,
                                      project_id,
                                      location,
                                      data_store_id)

    # create search engine
    operation = create_search_engine(q_engine, project_id, data_store_id)
    wait_for_operation(operation)
    Logger.info(f"Created vertex search engine for {q_engine.name}")

    # save metadata for datastore in query engine
    q_engine.index_id = data_store_id
    q_engine.update()

    # create QueryDocument models for processed documents
    for doc in docs_processed:
      query_document = QueryDocument(
        query_engine_id=q_engine.id,
        query_engine=q_engine.name,
        doc_url=doc.src_url,
        index_file=doc.gcs_path
      )
      query_document.save()
      doc_models_processed.append(query_document)

  except Exception as e:
    Logger.error(f"Error building vertex search query engine [{str(e)}]")
    Logger.error(traceback.print_exc())

    # on build error, delete any vertex search assets that were created
    delete_vertex_search(q_engine, data_store_id)
    raise e

  return doc_models_processed, docs_not_processed

def create_data_store(q_engine: QueryEngine,
                      project_id: str,
                      data_store_id: str) -> Operation:

  # create datastore request
  parent = \
      f"projects/{project_id}/locations/global/collections/default_collection"
  content_config = discoveryengine.DataStore.ContentConfig.CONTENT_REQUIRED
  data_store = discoveryengine.DataStore(
      display_name=q_engine.name,
      industry_vertical="GENERIC",
      solution_types=["SOLUTION_TYPE_SEARCH"],
      content_config=content_config)

  ds_request = discoveryengine.CreateDataStoreRequest(
      parent=parent,
      data_store_id=data_store_id,
      data_store=data_store)

  # use client to create datastore
  dss_client = discoveryengine.DataStoreServiceClient()
  operation = dss_client.create_data_store(request=ds_request)

  return operation

def create_search_engine(q_engine: QueryEngine,
                         project_id: str,
                         data_store_id: str) -> Operation:
  # create engine request
  parent = \
      f"projects/{project_id}/locations/global/collections/default_collection"
  engine = discoveryengine.Engine()
  engine.display_name = q_engine.name
  engine.solution_type = "SOLUTION_TYPE_SEARCH"
  engine.data_store_ids = [data_store_id]
  request = discoveryengine.CreateEngineRequest(parent=parent,
                                                engine=engine,
                                                engine_id=data_store_id)

  # use client to create engine
  es_client = discoveryengine.EngineServiceClient()
  operation = es_client.create_engine(request=request)

  return operation

def import_documents_to_datastore(data_url: str,
                                  docs_to_be_processed: List[DataSourceFile],
                                  project_id: str,
                                  location: str,
                                  data_store_id: str) -> \
                                      Tuple[List[str], List[str]]:
  """
  Import documents to a vertex search datastore.  Supports importing
  BQ dataset:table or GCS bucket containing docs.
  
  Args:
    data_url: url of data source (gcs, bq dataset:table)
    docs_to_be_processed: list of datasource file objects stored in the
       data url that should be imported
    project_id: id of project of datastore
    location: location of datastore (currently hard coded to "global")
       see: https://cloud.google.com/vertex-ai/docs/general/locations
       for more information
    data_store_id: id of datastore
  Returns:
    Tuple of (list of document urls that were imported from the data source,
              list of document urls that failed to import)
  """

  docs_processed = []
  docs_not_processed = []

  # create doc service client
  client_options = (
      ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
      if location != "global"
      else None
  )
  client = discoveryengine.DocumentServiceClient(client_options=client_options)

  # The full resource name of the search engine branch, e.g.
  # "projects/{project}/locations/{location}/dataStores/{data_store_id}"
  # + "/branches/{branch}"
  parent = client.branch_path(
      project=project_id,
      location=location,
      data_store=data_store_id,
      branch="default_branch",
  )

  # create operation to import data
  operation = None
  if data_url.startswith("gs://"):
    doc_gcs_urls = [doc.gcs_path for doc in docs_to_be_processed]
    operation = import_documents_gcs(doc_gcs_urls, client, parent)

  elif data_url.startswith("bq://"):
    bq_datasource = data_url.split("bq://")[1].split("/")[0]
    bigquery_dataset = bq_datasource.split(":")[0]
    bigquery_table = bq_datasource.split(":")[1]

    operation = import_documents_bq(project_id,
                                    bigquery_dataset,
                                    bigquery_table,
                                    client, parent)
    docs_processed = docs_to_be_processed

  Logger.info(
      f"Waiting for import operation to complete: {operation.operation.name}")
  wait_for_operation(operation)

  Logger.info(f"document import result: {operation.result}")

  # get information from operation metadata
  metadata = discoveryengine.ImportDocumentsMetadata(operation.metadata)

  # Handle the response
  Logger.info(f"document metadata from import: {metadata}")
  if metadata.success_count == len(docs_to_be_processed):
    docs_processed = docs_to_be_processed
  else:
    # TODO: build list of documents processed/not processed from results
    docs_processed = docs_to_be_processed

  return docs_processed, docs_not_processed


def import_documents_gcs(docs_to_be_processed: List[str],
                         client, parent) -> Tuple[List[str], Operation]:

  """ Import documents in a GCS bucket into a VSC Datastore """

  request = discoveryengine.ImportDocumentsRequest(
      parent=parent,
      gcs_source=discoveryengine.GcsSource(
          input_uris=docs_to_be_processed, data_schema="content"
      ),
      # Options: `FULL`, `INCREMENTAL`
      reconciliation_mode=\
        discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
  )

  # Make the request
  operation = client.import_documents(request=request)

  return operation

def import_documents_bq(project_id: str,
                        bigquery_dataset: str,
                        bigquery_table: str,
                        client, parent) -> Operation:

  request = discoveryengine.ImportDocumentsRequest(
      parent=parent,
      bigquery_source=discoveryengine.BigQuerySource(
          project_id=project_id,
          dataset_id=bigquery_dataset,
          table_id=bigquery_table,
          data_schema="custom",
      ),
      # Options: `FULL`, `INCREMENTAL`
      reconciliation_mode=\
        discoveryengine.ImportDocumentsRequest.ReconciliationMode.INCREMENTAL,
  )

  # Make the request
  operation = client.import_documents(request=request)

  return operation

def wait_for_operation(operation):
  if operation.done():
    result = None
  else:
    # wait for result
    result = operation.result(timeout=10000)
  return result

def datastore_id_from_engine(q_engine: QueryEngine) -> str:
  """ generate a valid datastore id from a query engine name """
  data_store_id = q_engine.name.lower()
  data_store_id = data_store_id.replace(" ", "-")
  if not re.fullmatch("[a-z0-9][a-z0-9-_]*", data_store_id):
    raise RuntimeError("Invalid datastore id: {data_store_id}")
  return data_store_id

def delete_vertex_search(q_engine: QueryEngine, data_store_id: str=None):
  """ attempt to delete a vertex search datastore and engine """
  Logger.info(f"deleting vertex search query engine {q_engine.name}")
  if data_store_id is None:
    data_store_id = q_engine.index_id
  try:
    Logger.info(f"deleting engine {q_engine.name}")
    client = discoveryengine.EngineServiceClient()
    request = discoveryengine.DeleteEngineRequest(name=q_engine.name)
    operation = client.delete_engine(request=request)
    wait_for_operation(operation)
    Logger.info(f"successfully deleted engine {q_engine.name}")
  except Exception as e:
    Logger.error(f"Exception deleting datastore {data_store_id}: {str(e)}")

  if data_store_id:
    try:
      Logger.info(f"deleting datastore {data_store_id}")
      client = discoveryengine.DataStoreServiceClient()
      request = discoveryengine.DeleteDataStoreRequest(name=data_store_id)
      operation = client.delete_data_store(request=request)
      wait_for_operation(operation)
      Logger.info(f"successfully deleted datastore {data_store_id}")
    except Exception as e:
      Logger.error(f"Exception deleting datastore {data_store_id}: {str(e)}")

def inventory_gcs_files(gcs_url: str) -> List[DataSourceFile]:
  """ create a list of eligible files for vertex search in the GCS bucket """
  valid_files = []
  storage_client = storage.Client(project=PROJECT_ID)
  bucket_name = gcs_url.split("gs://")[1].split("/")[0]
  for blob in storage_client.list_blobs(bucket_name):
    file_name = blob.name
    file_extension = Path(file_name).suffix
    if file_extension in VALID_FILE_EXTENSIONS:
      file_url = f"gs://{bucket_name}/{file_name}"
      doc = DataSourceFile(doc_name=Path(file_name).name,
                           src_url=file_url,
                           gcs_path=file_url)
      valid_files.append(doc)
  return valid_files

def download_web_docs(q_engine: QueryEngine, data_url: str) -> \
    Tuple[str, List[DataSourceFile]]:
  """
  Download web docs to a GCS bucket.
  Args:
    q_engine: QueryEngine (used for build params, i.e. depth_limit)
    data_url: http(s) url of root web page
  Returns:
    gcs_url:  URL of bucket holding files
              (bucket will be created if it doesn't exist)
    downloaded_docs: list of DataSourceFiles representing downloaded web docs
  """
  storage_client = storage.Client(project=PROJECT_ID)
  params = q_engine.params or {}
  if "depth_limit" in params:
    depth_limit = params["depth_limit"]
  else:
    depth_limit = DEFAULT_WEB_DEPTH_LIMIT

  # create web datasource
  bucket_name = WebDataSource.downloads_bucket_name(q_engine.name)
  web_data_source = WebDataSource(storage_client,
                                  bucket_name=bucket_name,
                                  depth_limit=depth_limit)

  # download web docs to GCS
  Logger.info(f"downloading web docs to bucket [{bucket_name}]")
  with tempfile.TemporaryDirectory() as temp_dir:
    downloaded_docs = web_data_source.download_documents(data_url, temp_dir)
  gcs_url = f"gs://{bucket_name}"
  return gcs_url, downloaded_docs
