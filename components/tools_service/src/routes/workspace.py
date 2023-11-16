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

""" Email tools endpoints """

from fastapi import APIRouter
from schemas.email import EmailSchema, EmailComposeSchema
from services.gmail_service import send_email
from services.email_composer import compose_email

router = APIRouter(prefix="/workspace", tags=["workspace"])

SUCCESS_RESPONSE = {"status": "Success"}


@router.post("/gmail")
async def gmail_send_email(data: EmailSchema):
  """Send an email using Gmail sevice.

  Args:
    data (str): A JSON string data.

  Raises:
    HTTPException: 500 Internal Server Error if something fails
  """

  result = send_email(data.recipient, data.subject, data.message)

  return {
    "recipient": data.recipient,
    "subject": data.subject,
    "result": result,
    "status": "Success",
  }


@router.post("/compose_email")
async def compose_email_subject_and_message(data: EmailComposeSchema):
  """Send an email using Gmail sevice.

  Args:
    data (str): A JSON string data.

  Raises:
    HTTPException: 500 Internal Server Error if something fails
  """

  result = compose_email(data.prompt, data.email_template, data.variables)

  print(result)

  return {
    "subject": result["subject"],
    "message": result["message"],
    "status": "Success",
  }
