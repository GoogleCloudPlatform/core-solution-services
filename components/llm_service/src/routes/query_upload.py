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

# pylint: disable = broad-except

""" Query Upload endpoints """
import traceback
from fastapi import APIRouter, Depends
from google.cloud import storage
from common.models import (QueryEngine, User, UserQuery)
from common.utils.auth_service import validate_token
from common.utils.errors import ValidationError, ResourceNotFoundException
from common.utils.http_exceptions import InternalServerError, BadRequest
from common.utils.logging_handler import Logger
from config import (ERROR_RESPONSES, get_model_config_value,
                    DEFAULT_MULTI_LLM_TYPE, KEY_IS_MULTI)
from schemas.llm_schema import QueryUploadGenerateModel, QueryUploadResponse
from services.query.query_service import query_upload_generate, update_user_query
from utils.gcs_helper import upload_file_to_gcs
from utils.file_helper import process_upload_file

Logger = Logger.get_logger(__file__)
router = APIRouter(prefix="/query", tags=["Query"], responses=ERROR_RESPONSES)

async def validate_query_file(query_file, query_file_url, bucket=None):
  query_file_name = None
  query_file_contents = None
  if query_file is not None:
    if query_file_url is not None:
      raise ValidationError("cannot set both query_file and query_file_url")
    query_file_url = await process_upload_file(query_file, bucket)
    query_file_name = query_file.filename
    query_file_contents = query_file.file
  elif query_file_url:
    if not (query_file_url.startswith("gs://")
            or query_file_url.startswith("http://")
            or query_file_url.startswith("https://")
            or query_file_url.startswith("shpt://")):
      return BadRequest(
          "query_file_url must start with gs://, http:// or https://, shpt://")
  else:
    raise ValidationError("must include query_file or query_file_url")
  return query_file_url, query_file_name, query_file_contents

@router.post(
    "/upload/generate",
    name="Upload file and execute a query",
    response_model=QueryUploadResponse)
async def query_file_upload(gen_config: QueryUploadGenerateModel,
                            user_data: dict = Depends(validate_token)):
  """
  Upload a file for querying.
  Can be used to upload files for building or querying.

  Args:
      gen_config (QueryUploadGenerateModel): dict
      user_data (dict)
  Returns:
      QueryUploadResponse
  """

  genconfig_dict = {**gen_config.dict()}
  prompt = gen_config["prompt"]
  llm_type = genconfig_dict.get("llm_type", None)
  query_file = genconfig_dict.get("query_file", None)
  query_file_url = genconfig_dict.get("query_file_url", None)

  Logger.info(f"Upload file and run query with {genconfig_dict}")
  try:
    # validate llm_type
    if llm_type is None:
      # use default multimodal model if not specified
      llm_type = DEFAULT_MULTI_LLM_TYPE
      Logger.info(f"using default multimodal llm_type [{llm_type}]")
    else:
      # validate that requested model is multimodal
      is_multi_modal = get_model_config_value(llm_type, KEY_IS_MULTI, False)
      if not is_multi_modal:
        raise ValidationError(f"llm_type [{llm_type}] is not multimodal")

    user = User.find_by_email(user_data.get("email"))

    query_file_url, query_file_name, query_file_contents = \
        await validate_query_file(query_file, query_file_url)

    # run query
    query_result, query_references = \
        query_upload_generate(user.id,
                              prompt,
                              llm_type,
                              query_file_name,
                              query_file_contents,
                              query_file_url)
    q_engine = QueryEngine.find_by_id(query_result.query_engine_id)

    # save user query history
    user_query, query_reference_dicts = \
        update_user_query(prompt,
                          query_result.response,
                          user.id,
                          q_engine,
                          query_references,
                          None,
                          None)

    response = {
      "success": True,
      "message": f"Successfully queried file {query_file}",
      "data": {
          "user_query_id": user_query.id,
          "query_result": query_result,
          "query_references": query_reference_dicts
      }
    }
    return response
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e


@router.post(
    "/upload/generate/{user_query_id}",
    name="Upload file and continue a query",
    response_model=QueryUploadResponse)
async def query_file_upload_continue(user_query_id: str,
                                     gen_config: QueryUploadGenerateModel,
                                     user_data: dict = Depends(validate_token)):
  """
  Upload a file for querying with an existing query.

  Args:
      user_query_id: str
      query_file: UploadFile
      gen_config (QueryUploadGenerateModel): dict
      user_data (dict)
  Returns:
      QueryUploadResponse
  """

  genconfig_dict = {**gen_config.dict()}
  prompt = gen_config["prompt"]
  llm_type = genconfig_dict.get("llm_type", None)
  query_file = genconfig_dict.get("query_file", None)
  query_file_url = genconfig_dict.get("query_file_url", None)

  Logger.info(f"Upload file and continue query with {genconfig_dict}")
  try:
    user = User.find_by_email(user_data.get("email"))

    # get existing user query and query engine
    user_query = UserQuery.find_by_id(user_query_id)
    if user_query is None:
      raise ResourceNotFoundException(f"User query {user_query_id} not found")
    q_engine = QueryEngine.find_by_id(user_query.query_engine_id)

    # get existing bucket
    data_url = q_engine.data_url
    if not data_url.startswith("gs://"):
      return BadRequest(
          "for query upload, query engine data URL must start with gs://")
    bucket_name = data_url[5:]
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    query_file_url, query_file_name, query_file_contents = \
        await validate_query_file(query_file, query_file_url, bucket=bucket)

    # upload file to bucket
    query_file_url = \
        upload_file_to_gcs(bucket, query_file.filename, query_file.file)

    # run query
    query_result, query_references = \
        query_upload_generate(user.id,
                              prompt,
                              llm_type,
                              query_file_name,
                              query_file_contents,
                              query_file_url)
    # save user query history
    user_query, query_reference_dicts = \
        update_user_query(prompt,
                          query_result.response,
                          user.id,
                          q_engine,
                          query_references,
                          user_query,
                          None)

    response = {
      "success": True,
      "message": f"Successfully queried file {query_file}",
      "data": {
          "user_query_id": user_query.id,
          "query_result": query_result,
          "query_references": query_reference_dicts
      }
    }
    return response
  except ValidationError as e:
    raise BadRequest(str(e)) from e
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e
