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
import os
import re
import tempfile
from copy import copy
from base64 import b64encode
from typing import List
from pathlib import Path
from common.utils.logging_handler import Logger
from common.models import QueryEngine
from config import PROJECT_ID
from langchain.text_splitter import CharacterTextSplitter
from pypdf import PdfReader, PdfWriter, PageObject
from pdf2image import convert_from_path
from langchain_community.document_loaders import CSVLoader
from utils.errors import NoDocumentsIndexedException
from utils import text_helper

# pylint: disable=broad-exception-caught

# text chunk size for embedding data
Logger = Logger.get_logger(__file__)
CHUNK_SIZE = 1000

class DataSourceFile():
  """ class storing meta data about a data source file """
  def __init__(self,
               doc_name:str,
               src_url:str,
               local_path:str,
               gcs_path:str = None):
    self.doc_name = doc_name
    self.src_url = src_url
    self.local_path = local_path
    self.gcs_path = gcs_path

class DataSource:
  """
  Super class for query data sources. Also implements GCS DataSource.
  """

  def __init__(self, storage_client):
    self.storage_client = storage_client
    self.docs_not_processed = []

  @classmethod
  def downloads_bucket_name(cls, q_engine: QueryEngine) -> str:
    qe_name = q_engine.name.replace(" ", "-")
    qe_name = qe_name.replace("_", "-").lower()
    bucket_name = f"{PROJECT_ID}-downloads-{qe_name}"
    if not re.fullmatch("^[a-z0-9][a-z0-9._-]{1,61}[a-z0-9]$", bucket_name):
      raise RuntimeError(f"Invalid downloads bucket name {bucket_name}")
    return bucket_name

  def download_documents(self, doc_url: str, temp_dir: str) -> \
        List[DataSourceFile]:
    """
    Download files from doc_url source to a local tmp directory

    Args:
        doc_url: url pointing to container of documents to be indexed
        temp_dir: Path to temporary directory to download files to

    Returns:
        list of DataSourceFile
    """
    doc_filepaths = []
    bucket_name = doc_url.split("gs://")[1].split("/")[0]
    Logger.info(f"downloading {doc_url} from bucket {bucket_name}")

    for blob in self.storage_client.list_blobs(bucket_name):
      # Download the file to the tmp folder flattening all directories
      file_name = Path(blob.name).name
      file_path = os.path.join(temp_dir, file_name)
      blob.download_to_filename(file_path)
      doc_filepaths.append(
          DataSourceFile(blob.name, blob.path, file_path, blob.path))

    if len(doc_filepaths) == 0:
      raise NoDocumentsIndexedException(
          f"No documents can be indexed at url {doc_url}")

    return doc_filepaths

  def chunk_document(self, doc_name: str, doc_url: str,
                     doc_filepath: str) -> List[str]:
    """
    Process doc into chunks for embeddings

    Args:
       doc_name: file name of document
       doc_url: remote url of document
       doc_filepath: local file path of document
    Returns:
       list of text chunks or None if the document could not be processed
    """

    text_chunks = None

    # use langchain text splitter
    text_splitter = CharacterTextSplitter(chunk_size=CHUNK_SIZE,
                                          chunk_overlap=0)

    Logger.info(f"generating index data for {doc_name}")

    # read doc data and split into text chunks
    # skip any file that can't be read or generates an error
    doc_text_list = None
    try:
      doc_text_list = self.read_doc(doc_name, doc_filepath)
      if doc_text_list is None:
        Logger.error(f"no content read from {doc_name}")
        self.docs_not_processed.append(doc_url)
    except Exception as e:
      Logger.error(f"error reading doc {doc_name}: {e}")
      self.docs_not_processed.append(doc_url)

    if doc_text_list is not None:
      # split text into chunks
      text_chunks = []
      for text in doc_text_list:
        text_chunks.extend(text_splitter.split_text(text))

      if all(element == "" for element in text_chunks):
        Logger.warning(f"All extracted pages from {doc_name} are empty.")
        self.docs_not_processed.append(doc_url)

      # clean up text_chunks with empty items.
      text_chunks = [x for x in text_chunks if x.strip() != ""]

      # clean text of escape and other unprintable chars
      text_chunks = [self.clean_text(x) for x in text_chunks]

    return text_chunks

  def chunk_document_multi(self, doc_name: str, doc_url: str,
                     doc_filepath: str) -> List[str]:
    """
    Process a pdf document into multimodal chunks (b64 and text) for embeddings

    Args:
       doc_name: file name of document
       doc_url: remote url of document
       doc_filepath: local file path of document
    Returns:
       array where each item is an object representing a page of the document
       contains two properties for image b64 data & text chunks 
       or None if the document could not be processed
    """
    Logger.info(f"generating index data for {doc_name}")

    # Confirm that this is a PDF
    try:
      doc_extension = doc_name.split(".")[-1]
      doc_extension = doc_extension.lower()
      if doc_extension != "pdf":
        raise ValueError(f"File {doc_name} must be a PDF")
    except Exception as e:
      Logger.error(f"error reading doc {doc_name}: {e}")

    doc_chunks = []
    try:
      # Convert PDF to an array of PNGs for each page
      png_array = None
      with tempfile.TemporaryDirectory() as path:
        png_array = convert_from_path(doc_filepath, output_folder=path)
      # Open PDF and iterate over pages
      with open(doc_filepath, "rb") as f:
        reader = PdfReader(f)
        num_pages = len(reader.pages)
        Logger.info(f"Reading pdf doc {doc_name} with {num_pages} pages")
        for i in range(num_pages):
          # Create a pdf file for the page and chunk into text chunks
          pdf_doc = self.create_pdf_page(reader.pages[i], doc_filepath, i)
          text_chunks = self.chunk_document(pdf_doc["filename"],
                                            doc_url, pdf_doc["filepath"])

          # Take PNG version of page and convert to b64
          png_doc_filepath = ".png".join(pdf_doc["filepath"].rsplit(".pdf", 1))
          png_array[i].save(png_doc_filepath, format="png")
          with open(png_doc_filepath, "rb") as f:
            png_bytes = f.read()
          png_b64 = b64encode(png_bytes).decode("utf-8")

          # Clean up temp files
          os.remove(pdf_doc["filepath"])
          os.remove(png_doc_filepath)

          # Push chunk object into chunk array
          chunk_obj = {
            "image_b64": png_b64,
            "text_chunks": text_chunks
          }
          doc_chunks.append(chunk_obj)
    except Exception as e:
      Logger.error(f"error processing doc {doc_name}: {e}")

    # Return array of page data
    return doc_chunks

  @classmethod
  def text_to_sentence_list(cls, text: str) -> List[str]:
    """
    Split text into sentences. 
    In this class we assume generic text.
    Subclasses may do additional transformation (e.g. html to text).
    """
    return text_helper.text_to_sentence_list(text)

  @classmethod
  def clean_text(cls, text: str) -> List[str]:
    """
    Produce clean text from text extracted from source document. 
    In this class we assume generic text.
    Subclasses may do additional transformation (e.g. html to text).
    """
    return text_helper.clean_text(text)

  @staticmethod
  def read_doc(doc_name: str, doc_filepath: str) -> List[str]:
    """
    Read document and return content as a list of strings

    Args:
      doc_name: name of document
      doc_filepath: local file path
    Returns:
      doc content as a list of strings
    """
    doc_extension = doc_name.split(".")[-1]
    doc_extension = doc_extension.lower()
    doc_text_list = None
    loader = None

    text_doc_extensions = ["txt", "html", "htm"]

    if doc_extension in text_doc_extensions:
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
      doc_text_list = [section.page_content for section in langchain_document]

    return doc_text_list

  @staticmethod
  def create_pdf_page(page: PageObject, doc_filepath: str,
                       page_index: int) -> List[str]:
    """
    Read pypdf PageObject and create a new pdf file for that PageObject

    Args:
      page: PdfReader page object representing a page from a pdf file
      doc_filepath: string filepath of the pdf we are reading the page from
      page_index: int index for the page of doc_filepath file we are on
    Returns:
      obj containing strings of the filename and filepath of new pdf
    """

    # Get file name and temp folder path
    doc_folder_i = doc_filepath.rfind("/")
    if doc_folder_i == -1:
      doc_folder = ""
    else:
      doc_folder = doc_filepath[:doc_folder_i+1]
    doc_file = doc_filepath[doc_folder_i+1:]

    # create a new PDF file and add the cropped page to the new PDF file
    page_copy = copy(page)
    page_pdf = PdfWriter()
    page_pdf.add_page(page_copy)

    # write the new PDF file to a file
    page_pdf_filename = str(page_index) + doc_file
    page_pdf_filepath = doc_folder + page_pdf_filename
    with open(page_pdf_filepath, "wb") as f:
      page_pdf.write(f)

    return {
      "filename": page_pdf_filename,
      "filepath": page_pdf_filepath
    }
