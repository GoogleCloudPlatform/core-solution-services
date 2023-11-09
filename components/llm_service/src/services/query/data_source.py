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
"""
Query Data Sources
"""
from pathlib import Path
from common.utils.logging_handler import Logger
from langchain.text_splitter import CharacterTextSplitter
from langchain.document_loaders import CSVLoader
from pypdf import PdfReader
from utils.errors import NoDocumentsIndexedException

# text chunk size for embedding data
CHUNK_SIZE = 1000

def download_documents(doc_url: str, temp_dir: Path) -> List[str]:

  # download files to local directory
  doc_filepaths = download_files_to_local(storage_client, temp_dir, doc_url)

  if len(doc_filepaths) == 0:
    raise NoDocumentsIndexedException(
        f"No documents can be indexed at url {doc_url}")
  return doc_filepaths


def chunk_document(doc_name: str, doc_url: str, doc_filepath: str) -> \
                    Tuple[List[QueryDocument], List[str]]:
  """
  Process docs at url and upload embeddings to GCS for indexing.
  Returns:
     Tuple of list of QueryDocument objects for docs processed,
        list of doc urls of docs not processed
  """

  # use langchain text splitter
  text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE,
                                        chunk_overlap=0)

  # add embeddings for each doc to index data stored in bucket
  docs_processed = []
  docs_not_processed = []

  Logger.info(f"generating index data for {doc_name}")

  # read doc data and split into text chunks
  # skip any file that can't be read or generates an error
  try:
    doc_text_list = read_doc(doc_name, doc_filepath)
    if doc_text_list is None:
      Logger.error(f"no content read from {doc_name}")
      docs_not_processed.append(doc_url)
      continue
  except Exception as e:
    Logger.error(f"error reading doc {doc_name}: {e}")
    docs_not_processed.append(doc_url)
    continue

  # split text into chunks
  text_chunks = []
  for text in doc_text_list:
    text_chunks.extend(text_splitter.split_text(text))

  if all(element == "" for element in text_chunks):
    Logger.warning(f"All extracted pages from {doc_name} are empty.")
    docs_not_processed.append(doc_url)
    continue

  return text_chunks


def download_files_to_local(storage_client, local_dir,
                             doc_url: str) -> List[Tuple[str, str, str]]:
  """ Download files from GCS to a local tmp directory """
  docs = []
  bucket_name = doc_url.split("gs://")[1].split("/")[0]
  Logger.info(f"downloading {doc_url} from bucket {bucket_name}")
  for blob in storage_client.list_blobs(bucket_name):
    # Download the file to the tmp folder flattening all directories
    file_name = Path(blob.name).name
    file_path = os.path.join(local_dir, file_name)
    blob.download_to_filename(file_path)
    docs.append((blob.name, blob.path, file_path))
  return docs


def read_doc(doc_name: str, doc_filepath: str) -> List[str]:
  """ Read document and return content as a list of strings """
  doc_extension = doc_name.split(".")[-1]
  doc_extension = doc_extension.lower()
  doc_text_list = None
  loader = None

  if doc_extension == "txt":
    with open(doc_filepath, "r", encoding="utf-8") as f:
      doc_text = f.read()
    doc_text_list = [doc_text]
  elif doc_extension == "csv":
    loader = CSVLoader(file_path=doc_filepath)
  elif doc_extension == "pdf":
    # read PDF into array of pages
    doc_text_list = []
    with open(doc_filepath, "rb") as f:
      reader = PdfReader(f)
      num_pages = len(reader.pages)
      Logger.info(f"Reading pdf file {doc_name} with {num_pages} pages")
      for page in range(num_pages):
        doc_text_list.append(reader.pages[page].extract_text())
      Logger.info(f"Finished reading pdf file {doc_name}")
  else:
    # return None if doc type not supported
    Logger.error(
        f"Cannot read {doc_name}: unsupported extension {doc_extension}")
    pass

  if loader is not None:
    langchain_document = loader.load()
    doc_text_list = [section.content for section in langchain_document]

  return doc_text_list
