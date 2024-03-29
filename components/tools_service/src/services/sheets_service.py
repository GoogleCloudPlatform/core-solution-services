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

"""Tools and utils for Google Sheets"""
import gspread
from common.utils.logging_handler import Logger
from utils.google_credential import get_google_sheets_credential

Logger = Logger.get_logger(__file__)

def create_spreadsheet(
    name: str, columns: list, rows: list,
    share_emails: list=None) -> dict:
  """
    Create spreadsheet with the given name an email to a recipient with message.
    Args:
       Name of the spreadsheet name : String
       List of User emails that this spreadsheet should be shared_with: List
       Column names of thte spreadsheet and rows as a List of
              columns : List
       Rows containing the values for the speadsheet as
              List of Lists rows : List
    Returns:
        Spreadsheet url and id type: Dict
  """
  #This function reads the secret from Google cloud, and saves it
  # locally to a tmp path
  file_path = get_google_sheets_credential()
  gc = gspread.service_account(filename=file_path)
  sh = gc.create(name)

  if share_emails:
    Logger.info(f"Sharing sheet {sh.id} with email(s): {share_emails}")
    recipients = ",".join(share_emails)
    sh.share(recipients, perm_type="user", role="writer")

  worksheet = sh.get_worksheet(0)
  #columns is a list of Strings of the column names
  if columns is not None:
    worksheet.append_row(columns, value_input_option="RAW")
  #rows is a list of lists, with each element of the outer list is a row of
  #values
  if rows is not None:
    worksheet.append_rows(rows,value_input_option="RAW")

  result =  {
    "sheet_url": sh.url,
    "sheet_id": sh.id
  }
  return result
