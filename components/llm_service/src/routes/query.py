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

# pylint: disable = broad-except

""" Query endpoints """
import traceback
from fastapi import APIRouter, Depends

from common.models import (QueryEngine,
                           User, UserQuery, QueryDocument)
from common.models.llm_query import QE_TYPE_INTEGRATED_SEARCH
from common.schemas.batch_job_schemas import BatchJobModel
from common.utils.auth_service import validate_token
from common.utils.batch_jobs import initiate_batch_job
from common.utils.config import (JOB_TYPE_QUERY_ENGINE_BUILD,
                                 JOB_TYPE_QUERY_EXECUTE)
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError,
                                 PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest,
                                          ResourceNotFound)
from common.utils.logging_handler import Logger
from config import (PROJECT_ID, DATABASE_PREFIX, PAYLOAD_FILE_SIZE,
                    ERROR_RESPONSES, ENABLE_OPENAI_LLM, ENABLE_COHERE_LLM,
                    DEFAULT_VECTOR_STORE, VECTOR_STORES, PG_HOST,
                    ONEDRIVE_CLIENT_ID, ONEDRIVE_TENANT_ID)
from schemas.llm_schema import (LLMQueryModel,
                                LLMUserAllQueriesResponse,
                                LLMUserQueryResponse,
                                UserQueryUpdateModel,
                                LLMQueryEngineModel,
                                LLMGetQueryEnginesResponse,
                                LLMQueryEngineURLResponse,
                                LLMQueryEngineResponse,
                                LLMQueryResponse,
                                LLMGetVectorStoreTypesResponse)
from services.query.query_service import (query_generate,
                                          delete_engine, update_user_query)
Logger = Logger.get_logger(__file__)
router = APIRouter(prefix="/query", tags=["Query"], responses=ERROR_RESPONSES)


@router.get(
    "",
    name="Get all Query engines",
    response_model=LLMGetQueryEnginesResponse)
def get_engine_list():
  """
  Get available Query engines

  Returns:
      LLMGetQueryEnginesResponse
  """
  query_engines = QueryEngine.fetch_all()
  query_engine_data = [{
    "id": qe.id,
    "name": qe.name,
    "query_engine_type": qe.query_engine_type,
    "doc_url": qe.doc_url,
    "description": qe.description,
    "read_access_group": qe.read_access_group,
    "llm_type": qe.llm_type,
    "embedding_type": qe.embedding_type,
    "vector_store": qe.vector_store,
    "params": qe.params,
    "created_time": qe.created_time,
    "last_modified_time": qe.last_modified_time,
  } for qe in query_engines]
  try:
    return {
      "success": True,
      "message": "Successfully retrieved query engine types",
      "data": query_engine_data
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.get(
    "/vectorstore",
    name="Get supported vector store types",
    response_model=LLMGetVectorStoreTypesResponse)
def get_vector_store_list():
  """
  Get available Vector Stores

  Returns:
      LLMGetVectorStoreTypesResponse
  """
  try:
    return {
      "success": True,
      "message": "Successfully retrieved vector store types",
      "data": VECTOR_STORES
    }
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.get(
  "/urls/{query_engine_id}",
  name="Get all URLs for a query engine",
  response_model=LLMQueryEngineURLResponse)
def get_urls_for_query_engine(query_engine_id: str):
  """
  Get all doc/web URLs for a Query Engine
  Args:
    query_engine_id (str):
  Returns:
      LLMQueryEngineURLResponse
  """
  try:
    Logger.info(f"Get all URLs for a Query Engine={query_engine_id}")

    # other user queries
    q_engine = QueryEngine.find_by_id(query_engine_id)
    if q_engine is None:
      raise ResourceNotFoundException(f"Engine {query_engine_id} not found")

    query_docs = QueryDocument.find_by_query_engine_id(query_engine_id)

    url_list = list(map(lambda query_doc: query_doc.doc_url, query_docs))
    return {
      "success": True,
      "message": "Successfully retrieved document URLs "
                 f"for query engine {query_engine_id}",
      "data": url_list
    }
  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

@router.get(
  "/engine/{query_engine_id}",
  name="Get details for query engine",
  response_model=LLMQueryEngineResponse)
def get_query_engine(query_engine_id: str):
  """
  Get details for a Query Engine
  Args:
    query_engine_id (str):
  Returns:
      LLMQueryEngineResponse
  """
  try:
    Logger.info(f"Get details for a Query Engine={query_engine_id}")

    # get engine model
    q_engine = QueryEngine.find_by_id(query_engine_id)
    if q_engine is None:
      raise ResourceNotFoundException(f"Engine {query_engine_id} not found")

    # get query docs
    query_docs = QueryDocument.find_by_query_engine_id(query_engine_id)
    url_list = list(map(lambda query_doc: query_doc.doc_url, query_docs))

    response_data = q_engine.get_fields(reformat_datetime=True)
    response_data["url_list"] = url_list
    return {
      "success": True,
      "message": "Successfully retrieved details "
                 f"for query engine {query_engine_id}",
      "data": response_data
    }
  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.get(
    "/user",
    name="Get all Queries for current logged-in user",
    response_model=LLMUserAllQueriesResponse)
def get_query_list(skip: int = 0,
                   limit: int = 20,
                   user_data: dict = Depends(validate_token)):
  """
  Get user queries for authenticated user.  Query data does not include
  history to slim payload.  To retrieve query history use the
  get single query endpoint.

  Args:
    user_id (str):
    skip (int): Number of tools to be skipped <br/>
    limit (int): Size of tools array to be returned <br/>

  Returns:
      LLMUserAllQueriesResponse
  """
  try:
    user_email = user_data.get("email")
    Logger.info(f"Get all Queries for a user={user_email}")
    if skip < 0:
      raise ValidationError("Invalid value passed to \"skip\" query parameter")

    if limit < 1:
      raise ValidationError("Invalid value passed to \"limit\" query parameter")

    user = User.find_by_email(user_email)
    if user is None:
      raise ResourceNotFoundException(f"User {user_email} not found ")

    user_queries = UserQuery.find_by_user(user.id, skip=skip, limit=limit)

    query_list = []
    for i in user_queries:
      query_data = i.get_fields(reformat_datetime=True)
      query_data["id"] = i.id
      # don't include chat history to slim return payload
      del query_data["history"]
      query_list.append(query_data)

    Logger.info(f"Successfully retrieved {len(query_list)} user queries.")
    return {
      "success": True,
      "message": f"Successfully retrieved user queries for user {user.id}",
      "data": query_list
    }
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.get(
    "/{query_id}",
    name="Get user query",
    response_model=LLMUserQueryResponse)
def get_query(query_id: str):
  """
  Get a specific user query by id

  Returns:
      LLMUserQueryResponse
  """
  try:
    Logger.info(f"Get a specific user query  by id={query_id}")
    user_query = UserQuery.find_by_id(query_id)
    query_data = user_query.get_fields(reformat_datetime=True)
    query_data["id"] = user_query.id

    Logger.info(f"Successfully retrieved user query {query_id}")
    return {
      "success": True,
      "message": f"Successfully retrieved user query {query_id}",
      "data": query_data
    }
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except ResourceNotFoundException as e:
    raise ResourceNotFound(str(e)) from e
  except Exception as e:
    raise InternalServerError(str(e)) from e


@router.put(
  "/{query_id}",
  name="Update user query"
)
def update_query(query_id: str, input_query: UserQueryUpdateModel):
  """Update a user query

  Args:
    query_id (str): Query ID
    input_query (UserQueryUpdateModel): fields in body of query to update.
      The only field that can be updated is the title.

  Raises:
    ResourceNotFoundException: If the UserQuery does not exist
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [JSON]: {'success': 'True'} if the user query is updated,
    NotFoundErrorResponseModel if the user query not found,
    InternalServerErrorResponseModel if the update raises an exception
  """
  Logger.info(f"Update a user query by id={query_id}")
  existing_query = UserQuery.find_by_id(query_id)
  if existing_query is None:
    raise ResourceNotFoundException(f"Query {query_id} not found")

  try:
    input_query_dict = {**input_query.dict()}

    for key in input_query_dict:
      if input_query_dict.get(key) is not None:
        setattr(existing_query, key, input_query_dict.get(key))
    existing_query.update()

    return {
      "success": True,
      "message": f"Successfully updated user query {query_id}",
    }
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e

@router.delete(
  "/{query_id}",
  name="Delete user query"
)
def delete_query(query_id: str, hard_delete: bool = True):
  """Delete a user query. By default we do a hard delete.

  Args:
    query_id (str): Query ID

  Raises:
    ResourceNotFoundException: If the UserQuery does not exist
    HTTPException: 500 Internal Server Error if something fails

  Returns:
    [JSON]: {'success': 'True'} if the user query is deleted,
    NotFoundErrorResponseModel if the user query not found,
    InternalServerErrorResponseModel if the update raises an exception
  """
  Logger.info(f"Delete a user query by id={query_id} hard_delete={hard_delete}")
  existing_query = UserQuery.find_by_id(query_id)
  if existing_query is None:
    raise ResourceNotFoundException(f"Query {query_id} not found")

  try:
    if hard_delete:
      UserQuery.delete_by_id(existing_query.id)
    else:
      UserQuery.soft_delete_by_id(existing_query.id)

    return {
      "success": True,
      "message": f"Successfully deleted user query {query_id}",
    }
  except ResourceNotFoundException as re:
    raise ResourceNotFound(str(re)) from re
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

@router.put(
  "/engine/{query_engine_id}",
  name="Update a query engine")
def update_query_engine(query_engine_id: str,
                        data_config: LLMQueryEngineModel):
  """
  Update a query engine. It only supports updating description
  and read access group.

  Args:
      query_engine_id (LLMQueryEngineModel)
  Returns:
    [JSON]: {'success': 'True'} if the query engine is deleted,
    ResourceNotFoundException if the query engine not found,
    InternalServerErrorResponseModel if the deletion raises an exception
  """
  if query_engine_id is None or query_engine_id == "":
    return BadRequest("Missing or invalid payload parameters: query_engine_id")

  q_engine = QueryEngine.find_by_id(query_engine_id)
  if q_engine is None:
    raise ResourceNotFoundException(f"Engine {query_engine_id} not found")

  data_dict = {**data_config.dict()}

  try:
    Logger.info(f"Updating q_engine=[{q_engine.name}]")
    q_engine.description = data_dict["description"]
    q_engine.read_access_group = data_dict["read_access_group"]
    q_engine.save()
    Logger.info(f"Successfully updated q_engine=[{q_engine.name}]")

  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e

  return {
    "success": True,
    "message": f"Successfully deleted query engine {query_engine_id}",
  }


@router.delete(
  "/engine/{query_engine_id}",
  name="Delete a query engine")
def delete_query_engine(query_engine_id: str, hard_delete: bool = True):
  """
  Delete a query engine.  By default we do a hard delete.

  Args:
      query_engine_id (LLMQueryEngineModel)
      hard_delete (boolean)
  Returns:
    [JSON]: {'success': 'True'} if the query engine is deleted,
    ResourceNotFoundException if the query engine not found,
    InternalServerErrorResponseModel if the deletion raises an exception
  """
  if query_engine_id is None or query_engine_id == "":
    return BadRequest("Missing or invalid payload parameters: query_engine_id")

  q_engine = QueryEngine.find_by_id(query_engine_id)
  if q_engine is None:
    raise ResourceNotFoundException(f"Engine {query_engine_id} not found")

  try:
    Logger.info(
        f"Deleting q_engine=[{q_engine.name}] hard_delete=[{hard_delete}]")

    delete_engine(q_engine, hard_delete=hard_delete)

    Logger.info(f"Successfully deleted q_engine=[{q_engine.name}]")
  except Exception as e:
    Logger.error(e)
    raise InternalServerError(str(e)) from e

  return {
    "success": True,
    "message": f"Successfully deleted query engine {query_engine_id}",
  }


@router.post(
    "/engine",
    name="Create a query engine",
    response_model=BatchJobModel)
async def query_engine_create(gen_config: LLMQueryEngineModel,
                              user_data: dict = Depends(validate_token)):
  """
  Start a query engine build job

  Args:
      gen_config (LLMQueryEngineModel)
      user_data (dict)
  Returns:
      BatchJobModel
  """

  genconfig_dict = {**gen_config.dict()}

  Logger.info(f"Create a query engine with {genconfig_dict}")

  doc_url = genconfig_dict.get("doc_url")
  query_engine_type = genconfig_dict.get("query_engine_type", None)

  if query_engine_type != QE_TYPE_INTEGRATED_SEARCH:
    # validate doc_url
    if doc_url is None or doc_url == "":
      return BadRequest("Missing or invalid payload parameters: doc_url")

    if not (doc_url.startswith("gs://")
            or doc_url.startswith("http://")
            or doc_url.startswith("https://")
            or doc_url.startswith("bq://")
            or doc_url.startswith("shpt://")):
      return BadRequest(
          "doc_url must start with gs://, http:// or https://, bq://, shpt://")

    if doc_url.endswith(".pdf"):
      return BadRequest(
        "doc_url must point to a GCS bucket/folder or website, not a document")

  query_engine = genconfig_dict.get("query_engine")
  if query_engine is None or query_engine == "":
    return BadRequest("Missing or invalid payload parameters: query_engine")

  q_engine = QueryEngine.find_by_name(query_engine)
  if q_engine:
    return BadRequest(f"Query engine already exists: {query_engine}")

  user_id = user_data.get("user_id")

  params = genconfig_dict.get("params", {})

  try:
    data = {
      "doc_url": doc_url,
      "query_engine": query_engine,
      "user_id": user_id,
      "query_engine_type": query_engine_type,
      "llm_type": genconfig_dict.get("llm_type", None),
      "embedding_type": genconfig_dict.get("embedding_type", None),
      "vector_store": genconfig_dict.get("vector_store", None),
      "description": genconfig_dict.get("description", None),
      "params": params,
    }
    env_vars = {
      "DATABASE_PREFIX": DATABASE_PREFIX,
      "PROJECT_ID": PROJECT_ID,
      "ENABLE_OPENAI_LLM": str(ENABLE_OPENAI_LLM),
      "ENABLE_COHERE_LLM": str(ENABLE_COHERE_LLM),
      "DEFAULT_VECTOR_STORE": str(DEFAULT_VECTOR_STORE),
      "PG_HOST": PG_HOST,
      "ONEDRIVE_CLIENT_ID": ONEDRIVE_CLIENT_ID,
      "ONEDRIVE_TENANT_ID": ONEDRIVE_TENANT_ID,
    }
    response = initiate_batch_job(data, JOB_TYPE_QUERY_ENGINE_BUILD, env_vars)
    Logger.info(f"Batch job response: {response}")
    return response
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/engine/{query_engine_id}",
    name="Make a query to a query engine",
    response_model=LLMQueryResponse)
async def query(query_engine_id: str,
                gen_config: LLMQueryModel,
                user_data: dict = Depends(validate_token)):
  """
  Send a query to a query engine and return the response

  Args:
      query_engine_id (str):
      gen_config (LLMQueryModel):
      user_data (dict):

  Returns:
      LLMQueryResponse
  """
  Logger.info(f"Using query engine with "
              f"query_engine_id=[{query_engine_id}] and {gen_config}")
  q_engine = QueryEngine.find_by_id(query_engine_id)
  if q_engine is None:
    raise ResourceNotFoundException(f"Engine {query_engine_id} not found")

  genconfig_dict = {**gen_config.dict()}

  prompt = genconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  llm_type = genconfig_dict.get("llm_type")
  rank_sentences = genconfig_dict.get("rank_sentences", False)
  Logger.info(f"rank_sentences = {rank_sentences}")

  query_filter = genconfig_dict.get("query_filter")
  Logger.info(f"query_filter = {query_filter}")

  # get the User GENIE stores
  user = User.find_by_email(user_data.get("email"))

  run_as_batch_job = genconfig_dict.get("run_as_batch_job", False)
  Logger.info(f"run_as_batch_job = {run_as_batch_job}")

  user_query = None
  if run_as_batch_job:
    # create user query object to hold the query state
    user_query = UserQuery(user_id=user.user_id,
                           prompt=prompt, query_engine_id=q_engine.id)
    user_query.save()
    user_query.update_history(prompt=prompt)
    query_data = user_query.get_fields(reformat_datetime=True)
    query_data["id"] = user_query.id

    # launch batch job to perform query
    try:
      data = {
        "query_engine_id": query_engine_id,
        "prompt": prompt,
        "llm_type": llm_type,
        "user_id": user.id,
        "user_query_id": user_query.id,
        "rank_sentences": rank_sentences,
        "query_filter": query_filter
      }
      env_vars = {
        "DATABASE_PREFIX": DATABASE_PREFIX,
        "PROJECT_ID": PROJECT_ID,
        "ENABLE_OPENAI_LLM": str(ENABLE_OPENAI_LLM),
        "ENABLE_COHERE_LLM": str(ENABLE_COHERE_LLM),
        "DEFAULT_VECTOR_STORE": str(DEFAULT_VECTOR_STORE),
        "PG_HOST": PG_HOST,
      }
      response = initiate_batch_job(data, JOB_TYPE_QUERY_EXECUTE, env_vars)
      Logger.info(f"Batch job response: {response}")

      return {
        "success": True,
        "message": "Successfully ran query in batch mode",
        "data": {
          "query": query_data,
          "batch_job": response["data"],
        },
      }
    except Exception as e:
      Logger.error(e)
      Logger.error(traceback.print_exc())
      raise InternalServerError(str(e)) from e

  # perform normal synchronous query
  try:
    query_result, query_references = await query_generate(user.id,
                                                          prompt,
                                                          q_engine,
                                                          user_data,
                                                          llm_type,
                                                          user_query,
                                                          rank_sentences,
                                                          query_filter)

    Logger.info(f"Query response="
                f"[{query_result.response}]")

    # save user query history
    user_query, query_reference_dicts = \
        update_user_query(prompt,
                          query_result.response,
                          user.id,
                          q_engine,
                          query_references, None,
                          query_filter)

    query_result_dict = query_result.get_fields(reformat_datetime=True)

    return {
        "success": True,
        "message": "Successfully generated text",
        "data": {
            "user_query_id": user_query.id,
            "query_result": query_result_dict,
            "query_references": query_reference_dicts
        }
    }
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/{user_query_id}",
    name="Continue chat with a prior user query",
    response_model=LLMQueryResponse)
async def query_continue(
  user_query_id: str,
  gen_config: LLMQueryModel,
  user_data: dict = Depends(validate_token)):
  """
  Continue a prior user query.  Perform a new search and
  add those references along with prior query/chat history as context.

  Args:
      user_query_id (str): id of previous user query
      gen_config (LLMQueryModel)

  Returns:
      LLMQueryResponse
  """
  Logger.info("Using query engine based on a prior user query "
              f"user_query_id={user_query_id}, gen_config={gen_config}")
  user_query = UserQuery.find_by_id(user_query_id)
  if user_query is None:
    raise ResourceNotFoundException(f"Query {user_query_id} not found")

  genconfig_dict = {**gen_config.dict()}

  prompt = genconfig_dict.get("prompt")
  if prompt is None or prompt == "":
    return BadRequest("Missing or invalid payload parameters")

  if len(prompt) > PAYLOAD_FILE_SIZE:
    return PayloadTooLargeError(
      f"Prompt must be less than {PAYLOAD_FILE_SIZE}")

  llm_type = genconfig_dict.get("llm_type")

  rank_sentences = genconfig_dict.get("rank_sentences", False)
  Logger.info(f"rank_sentences = {rank_sentences}")

  query_filter = genconfig_dict.get("query_filter")
  Logger.info(f"query_filter = {query_filter}")

  q_engine = QueryEngine.find_by_id(user_query.query_engine_id)

  run_as_batch_job = genconfig_dict.get("run_as_batch_job", False)

  if run_as_batch_job:
    # launch batch job to perform query
    try:
      data = {
        "query_engine_id": q_engine.id,
        "prompt": prompt,
        "llm_type": llm_type,
        "user_id": user_query.user_id,
        "user_query_id": user_query.id,
        "rank_sentences": rank_sentences
      }
      env_vars = {
        "DATABASE_PREFIX": DATABASE_PREFIX,
        "PROJECT_ID": PROJECT_ID,
        "ENABLE_OPENAI_LLM": str(ENABLE_OPENAI_LLM),
        "ENABLE_COHERE_LLM": str(ENABLE_COHERE_LLM),
        "DEFAULT_VECTOR_STORE": str(DEFAULT_VECTOR_STORE),
        "PG_HOST": PG_HOST,
      }
      response = initiate_batch_job(data, JOB_TYPE_QUERY_EXECUTE, env_vars)
      Logger.info(f"Batch job response: {response}")

      query_data = user_query.get_fields(reformat_datetime=True)
      query_data["id"] = user_query.id

      return {
        "success": True,
        "message": "Successfully ran query in batch mode",
        "data": {
          "query": query_data,
          "batch_job": response["data"],
        },
      }
    except Exception as e:
      Logger.error(e)
      Logger.error(traceback.print_exc())
      raise InternalServerError(str(e)) from e

  # perform normal synchronous query
  try:
    query_result, query_references = await query_generate(user_query.user_id,
                                                          prompt,
                                                          q_engine,
                                                          user_data,
                                                          llm_type,
                                                          user_query,
                                                          rank_sentences,
                                                          query_filter)
    # save user query history
    _, query_reference_dicts = \
        update_user_query(prompt,
                          query_result.response,
                          user_query.user_id,
                          q_engine,
                          query_references)

    Logger.info(f"Generated query response="
                f"[{query_result.response}], "
                f"query_result={query_result} "
                f"query_references={[repr(qe) for qe in query_references]}")

    query_result_dict = query_result.get_fields(reformat_datetime=True)

    return {
        "success": True,
        "message": "Successfully generated text",
        "data": {
            "user_query_id": user_query.id,
            "query_result": query_result_dict,
            "query_references": query_reference_dicts
        }
    }

  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e
