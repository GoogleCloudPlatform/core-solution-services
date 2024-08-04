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

""" Query endpoints """
import traceback
from fastapi import APIRouter, Depends
from google.cloud import storage
from common.models import (QueryEngine,
                           User, UserQuery, QueryDocument)
from common.utils.auth_service import validate_token
from common.utils.errors import (ResourceNotFoundException,
                                 ValidationError,
                                 PayloadTooLargeError)
from common.utils.http_exceptions import (InternalServerError, BadRequest,
                                          ResourceNotFound)
from common.utils.logging_handler import Logger
from config import (PROJECT_ID, DATABASE_PREFIX, PAYLOAD_FILE_SIZE,
                    ERROR_RESPONSES)
from schemas.llm_schema import QueryUploadGenerateModel, QueryUploadResponse
from utils.gcs_helper import create_bucket_for_file, upload_file_to_gcs

Logger = Logger.get_logger(__file__)
router = APIRouter(prefix="/query", tags=["Query"], responses=ERROR_RESPONSES)

@router.post(
    "/upload/generate",
    name="Upload files and execute a query",
    response_model=QueryUploadResponse)
async def query_file_upload(query_file: UploadFile = File(...),
                            gen_config: QueryUploadGenerateModel,
                            user_data: dict = Depends(validate_token)):
  """
  Upload a file for querying.
  Can be used to upload files for building or querying.

  Args:
      query_file
      user_data (dict)
  Returns:
      QueryUploadResponse
  """

  genconfig_dict = {**gen_config.dict()}
  prompt = gen_config["prompt"]
  llm_type = genconfig_dict.get("llm_type", None)
  
  Logger.info(f"Upload file and run query with {genconfig_dict}")
  try:
    # read upload file
    if len(await query_file.read()) > PAYLOAD_FILE_SIZE:
      raise PayloadTooLargeError(
        f"File size is too large: {query_file.filename}"
      )
    await query_file.seek(0)

    # create bucket for file
    bucket = create_bucket_for_file(query_file.filename)

    # upload file to bucket
    query_file_url = \
        upload_file_to_gcs(bucket, query_file.filename, query_file.file)

    # run query
    user_query, query_result, query_references = \
        query_upload_generate(user_id,
                              prompt,
                              query_file_url,
                              user_data,
                              llm_type)
    response = {
      "success": True,
      "message": f"Successfully queried file {query_file}",
    }
    return response
  except Exception as e:
    Logger.error(e)
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e
