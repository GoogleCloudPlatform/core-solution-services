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
LLM Generation Service
"""
# pylint: disable=import-outside-toplevel,line-too-long
import time
import requests
import base64
from typing import Optional, List, AsyncGenerator, Union
import google.auth
import google.auth.transport.requests
import google.cloud.aiplatform
from openai import OpenAI, OpenAIError
from vertexai.preview.language_models import (ChatModel, TextGenerationModel)
from vertexai.preview.generative_models import (
    GenerativeModel, Part, GenerationConfig, HarmCategory, HarmBlockThreshold)
from common.config import PROJECT_ID, REGION
from common.models import UserChat, UserQuery
from common.utils.errors import ResourceNotFoundException
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import (post_method,
                                          DEFAULT_TIMEOUT)
from common.utils.token_handler import UserCredentials
from config import (get_model_config, get_provider_models,
                    get_provider_value, get_provider_model_config,
                    get_model_config_value,
                    PROVIDER_VERTEX, PROVIDER_TRUSS,
                    PROVIDER_MODEL_GARDEN, PROVIDER_VLLM,
                    PROVIDER_LANGCHAIN, PROVIDER_LLM_SERVICE,
                    KEY_MODEL_ENDPOINT, KEY_MODEL_NAME,
                    KEY_MODEL_PARAMS, KEY_MODEL_CONTEXT_LENGTH,
                    DEFAULT_LLM_TYPE, DEFAULT_MULTIMODAL_LLM_TYPE,
                    KEY_SUB_PROVIDER, SUB_PROVIDER_OPENAPI)
from services.langchain_service import langchain_llm_generate
from services.query.data_source import DataSourceFile
from utils.errors import ContextWindowExceededException

Logger = Logger.get_logger(__file__)

# A conservative characters-per-token constant, used to check
# whether prompt length exceeds context window size
CHARS_PER_TOKEN = 3

async def llm_generate(prompt: str, llm_type: str, stream: bool = False) -> \
    Union[str, AsyncGenerator[str, None]]:
  """
  Generate text with an LLM given a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use (default to openai)
    stream: whether to stream the response
  Returns:
    Either the full text response as str, or an AsyncGenerator yielding response chunks
  """
  Logger.info(f"Generating text with an LLM given a prompt={prompt},"
              f" llm_type={llm_type}")
  # default to openai LLM
  if llm_type is None:
    llm_type = DEFAULT_LLM_TYPE

  try:
    start_time = time.time()

    # check whether the context length exceeds the limit for the model
    check_context_length(prompt, llm_type)

    # call the appropriate provider to generate the chat response
    # for Google models, prioritize native client over langchain
    chat_llm_types = get_model_config().get_chat_llm_types()
    if llm_type in get_provider_models(PROVIDER_LLM_SERVICE):
      is_chat = llm_type in chat_llm_types
      response = await llm_service_predict(prompt, is_chat, llm_type)
    elif llm_type in get_provider_models(PROVIDER_TRUSS):
      model_endpoint = get_provider_value(
          PROVIDER_TRUSS, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_truss_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_VLLM):
      model_endpoint = get_provider_value(
          PROVIDER_VLLM, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_vllm_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_MODEL_GARDEN):
      response = await model_garden_predict(prompt, llm_type)
    elif llm_type in get_provider_models(PROVIDER_VERTEX):
      google_llm = get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      if google_llm is None:
        raise RuntimeError(
            f"Vertex model name not found for llm type {llm_type}")
      is_chat = llm_type in chat_llm_types
      is_multimodal = False
      response = await google_llm_predict(
        prompt, is_chat, is_multimodal, google_llm, stream=stream)
    elif llm_type in get_provider_models(PROVIDER_LANGCHAIN):
      response = await langchain_llm_generate(prompt, llm_type)
    else:
      raise ResourceNotFoundException(f"Cannot find llm type '{llm_type}'")

    process_time = round(time.time() - start_time)
    Logger.info(f"Received response in {process_time} seconds from "
                f"model with llm_type={llm_type}.")
    return response
  except Exception as e:
    raise InternalServerError(str(e)) from e

async def llm_generate_multimodal(prompt: str, llm_type: str,
                             user_file_bytes: bytes = None,
                             user_files: List[DataSourceFile] = None) -> str:
  """
  Generate text with an LLM given a file and a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use (default to gemini)
    user_file_bytes: bytes of the file provided by the user
    user_files: list of DataSourceFile objects for file meta data
  Returns:
    the text response: str
  """
  Logger.info(f"Generating text with an LLM given a prompt={prompt},"
              f" user_file_bytes=bytes, llm_type={llm_type}")
  # default to Gemini multimodal LLM
  if llm_type is None:
    llm_type = DEFAULT_MULTIMODAL_LLM_TYPE

  try:
    start_time = time.time()

    # for Google models, prioritize native client over langchain
    chat_llm_types = get_model_config().get_chat_llm_types()
    multimodal_llm_types = get_model_config().get_multimodal_llm_types()
    if llm_type in get_provider_models(PROVIDER_VERTEX):
      google_llm = get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      if google_llm is None:
        raise RuntimeError(
            f"Vertex model name not found for llm type {llm_type}")
      is_chat = llm_type in chat_llm_types
      is_multimodal = llm_type in multimodal_llm_types
      if not is_multimodal:
        raise RuntimeError(
            f"Vertex model {llm_type} needs to be multimodal")
      response = await google_llm_predict(prompt, is_chat, is_multimodal,
                            google_llm, None, user_file_bytes,
                            user_files)
    else:
      raise ResourceNotFoundException(f"Cannot find llm type '{llm_type}'")

    process_time = round(time.time() - start_time)
    Logger.info(f"Received response in {process_time} seconds from "
                f"model with llm_type={llm_type}.")
    return response
  except Exception as e:
    raise InternalServerError(str(e)) from e

async def llm_chat(prompt: str, llm_type: str,
                   user_chat: Optional[UserChat] = None,
                   user_query: Optional[UserQuery] = None,
                   chat_files: Optional[List[DataSourceFile]] = None,
                   chat_file_bytes: Optional[bytes] = None,
                   stream: bool = False) -> \
                       Union[str, AsyncGenerator[str, None]]:
  """
  Send a prompt to a chat model and return string response or stream.
  Supports including a file in the chat context, either by URL or
  directly from file content.

  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use
    user_chat (optional): a user chat to use for context
    user_query (optional): a user query to use for context
    chat_files (optional) (List[DataSourceFile]): files to include in chat context
    chat_file_bytes (optional) (bytes): bytes of file to include in chat context
    stream: whether to stream the response
  Returns:
    Either the full text response as str, or an AsyncGenerator
      yielding response chunks
  """
  chat_file_bytes_log = chat_file_bytes[:10] if chat_file_bytes else None
  Logger.info(f"Generating chat with llm_type=[{llm_type}],"
              f" prompt=[{prompt}]"
              f" user_chat=[{user_chat}]"
              f" user_query=[{user_query}]"
              f" chat_file_bytes=[{chat_file_bytes_log}]"
              f" chat_files=[{chat_files}]")

  if llm_type not in get_model_config().get_chat_llm_types():
    raise ResourceNotFoundException(f"Cannot find chat llm type '{llm_type}'")

  # validate chat file params
  is_multimodal = False
  if chat_file_bytes is not None or chat_files:
    if chat_file_bytes is not None and chat_files:
      raise InternalServerError(
          "Must set only one of chat_file_bytes/chat_files")
    if llm_type not in get_provider_models(PROVIDER_VERTEX):
      raise InternalServerError("Chat files only supported for Vertex")
    is_multimodal = True

  try:
    response = None

    # add chat history to prompt if necessary
    if user_chat is not None or user_query is not None:
      context_prompt = get_context_prompt(
          user_chat=user_chat, user_query=user_query)
      # context_prompt includes only text (no images/video) from
      # user_chat.history and user_query.history
      prompt = context_prompt + "\n" + prompt

    # check whether the context length exceeds the limit for the model
    check_context_length(prompt, llm_type)

    # call the appropriate provider to generate the chat response
    if llm_type in get_provider_models(PROVIDER_LLM_SERVICE):
      is_chat = True
      response = await llm_service_predict(
          prompt, is_chat, llm_type, user_chat)
    elif llm_type in get_provider_models(PROVIDER_TRUSS):
      model_endpoint = get_provider_value(
          PROVIDER_TRUSS, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_truss_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_VLLM):
      model_endpoint = get_provider_value(
          PROVIDER_VLLM, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_vllm_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in get_provider_models(PROVIDER_MODEL_GARDEN):
      response = await model_garden_predict(prompt, llm_type)
    elif llm_type in get_provider_models(PROVIDER_VERTEX):
      google_llm = get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      if google_llm is None:
        raise RuntimeError(
            f"Vertex model name not found for llm type {llm_type}")
      is_chat = True
      response = await google_llm_predict(prompt, is_chat, is_multimodal,
                                          google_llm, user_chat,
                                          chat_file_bytes, chat_files,
                                          stream=stream)
    elif llm_type in get_provider_models(PROVIDER_LANGCHAIN):
      response = await langchain_llm_generate(prompt, llm_type, user_chat)
    return response
  except Exception as e:
    import traceback
    Logger.error(traceback.print_exc())
    raise InternalServerError(str(e)) from e

def get_context_prompt(user_chat=None,
                       user_query=None) -> str:
  """
  Get context prompt for chat based on previous chat or query history.

  Args:
    user_chat (optional): previous user chat
    user_query (optional): previous user query
  Returns:
    string context prompt
  """
  context_prompt = ""
  prompt_list = []
  if user_chat is not None:
    history = user_chat.history
    for entry in history:
      content = UserChat.entry_content(entry)
      if UserChat.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserChat.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
      # prompt_list includes only text from user_chat.history

  if user_query is not None:
    history = user_query.history
    for entry in history:
      content = UserQuery.entry_content(entry)
      if UserQuery.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserQuery.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
      # prompt_list includes only text from user_query.history

  context_prompt = "\n\n".join(prompt_list)

  return context_prompt

def check_context_length(prompt, llm_type):
  """
  Check whether a prompt exceeds the maximum context length for
  a model.

  Raise an exception if max context length exceeded.
  """
  # check if prompt exceeds context window length for model
  # assume a constant relationship between tokens and chars
  # TODO: Recalculate max_context_length for text prompt,
  # subtracting out tokens used by non-text context (image, video, etc)
  token_length = len(prompt) / CHARS_PER_TOKEN
  max_context_length = get_model_config_value(llm_type,
                                              KEY_MODEL_CONTEXT_LENGTH,
                                              None)
  if max_context_length and token_length > max_context_length:
    msg = f"Token length {token_length} exceeds llm_type {llm_type} " + \
          f"Max context length {max_context_length}"
    Logger.error(msg)
    raise ContextWindowExceededException(msg)

async def llm_truss_service_predict(llm_type: str, prompt: str,
                                    model_endpoint: str,
                                    parameters: dict = None) -> str:
  """
  Send a prompt to an instance of the LLM service and return response.
  Args:
    llm_type:
    prompt: the text prompt to pass to the LLM
    model_endpoint: model endpoint ip to be used for prediction and port number
      (e.g: xx.xxx.xxx.xx:8080)
    parameters (optional):  parameters to be used for prediction
  Returns:
    the text response: str
  """
  if parameters is None:
    parameters = get_provider_value(
        PROVIDER_TRUSS, KEY_MODEL_PARAMS, llm_type)

  parameters.update({"prompt": f"'{prompt}'"})

  api_url = f"http://{model_endpoint}/v1/models/model:predict"
  Logger.info(f"Generating text using Truss Hosted Model "
              f"api_url=[{api_url}], prompt=[{prompt}], "
              f"parameters=[{parameters}.")

  resp = post_method(api_url, request_body=parameters)

  if resp.status_code != 200:
    raise InternalServerError(
      f"Error status {resp.status_code}: {str(resp)}")

  json_response = resp.json()

  Logger.info(f"Got LLM service response {json_response}")
  output = json_response["data"]["generated_text"]

  # if the prompt is repeated as part of the response, remove it
  output = output.replace(prompt, "").strip()
  # Llama 2 often adds quotes
  if output.startswith('"') or output.startswith("'"):
    output = output[1:]
  if output.endswith('"') or output.endswith("'"):
    output = output[:-1]

  return output

async def llm_vllm_service_predict(llm_type: str, prompt: str,
                                   model_endpoint: str,
                                   parameters: dict = None) -> str:
  """
  Send a prompt to an instance of the vllm service using the openai api.
  Assumes that the vllm server is only hosting a single model and will call the
  first model returned by client.models.list.
  Args:
    llm_type:
    prompt: the text prompt to pass to the LLM
    model_endpoint: model endpoint ip to be used for prediction and port number
      (e.g: xx.xxx.xxx.xx:8080)
    parameters (optional):  parameters to be used for prediction
  Returns:
    the text response: str
  """
  if parameters is None:
    parameters = get_provider_value(
        PROVIDER_VLLM, KEY_MODEL_PARAMS, llm_type)

  if parameters is None:
    parameter_kwargs = {}
  else:
    parameter_kwargs = dict(parameters)

  openai_api_key = "EMPTY"  # Not required for vLLM
  openai_api_base = f"http://{model_endpoint}/v1"

  client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
  )

  try:
    models = client.models.list()
    model = models.data[0].id

    Logger.info(f"Generating text using vLLM Hosted Model {model} hosted at"
            f"api_base=[{openai_api_base}], prompt=[{prompt}], "
            f"parameters=[{parameters}.")

    response = client.chat.completions.create(
        model=model,
        messages=[
          {"role": "user", "content": prompt}
        ],
        **parameter_kwargs
    )
    output = response.choices[0].message.content
    Logger.info(f"Got LLM service response {response}")

  except OpenAIError as e:
    Logger.error(f"OpenAI API error: {e}")
    raise InternalServerError(f"Error: {e}") from e

  return output


async def llm_service_predict(prompt: str, is_chat: bool,
                              llm_type: str, user_chat=None,
                              auth_token: str = None) -> str:

  """
  Send a prompt to an instance of the LLM service and return response.

  Args:
    prompt: the text prompt to pass to the LLM
    is_chat: true if the model is a chat model
    llm_type: the type of LLM to use
    user_chat (optional): a user chat to use for context
    auth_token:

  Returns:
    the text response: str
  """
  llm_service_config = get_model_config().get_provider_config(
      PROVIDER_LLM_SERVICE, llm_type)
  if not auth_token:
    auth_client = UserCredentials(llm_service_config.get("user"),
                                  llm_service_config.get("password"))
    auth_token = auth_client.get_id_token()

  # start with base url of the LLM service we are calling
  api_url = llm_service_config.get(KEY_MODEL_ENDPOINT)

  if is_chat:
    if user_chat:
      path = "/chat/{user_chat.id}"
    else:
      path = "/chat"
  else:
    path = "/llm/generate"
  api_url = api_url + path

  request_body = {
    "prompt": prompt,
    "llm_type": llm_type
  }

  Logger.info(f"Sending LLM service request to {api_url}")
  resp = post_method(api_url,
                     request_body=request_body,
                     token=auth_token)

  if resp.status_code != 200:
    raise InternalServerError(
      f"Error status {resp.status_code}: {str(resp)}")

  json_response = resp.json()

  Logger.info(f"Got LLM service response {json_response}")
  output = json_response["content"]
  return output

async def model_garden_predict(prompt: str,
                               llm_type: str,
                               parameters: dict = None) -> str:
  """
  Generate text with a Model Garden model.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type:
    parameters (optional):  parameters to be used for prediction
  Returns:
    the prediction text.
  """
  aip_endpoint_name = get_provider_value(
      PROVIDER_MODEL_GARDEN, KEY_MODEL_ENDPOINT, llm_type)

  sub_provider_name = get_provider_value(
      PROVIDER_MODEL_GARDEN, KEY_SUB_PROVIDER, llm_type)

  if str(sub_provider_name) == str(SUB_PROVIDER_OPENAPI):
    creds, _ = google.auth.default()
    if not creds.valid:
      auth_req = google.auth.transport.requests.Request()
      creds.refresh(auth_req)
    auth_token = creds.token

    openapi_endpoint = f"https://{REGION}-aiplatform.googleapis.com/" \
                       f"v1/projects/{PROJECT_ID}/locations/{REGION}/" \
                      f"endpoints/openapi/chat/completions"
    req_headers = {"Authorization": f"Bearer {auth_token}",
                   "Content-Type": "application/json"}
    req_body = {"model": f"{aip_endpoint_name}",
                "messages":[{"role": "user",
                             "content": f"{prompt}"}]}
    Logger.info(f"Generating text using OpenAPI for Model Garden "
              f"endpoint=[{openapi_endpoint}], req_headers=[{req_headers}], "
              f"req_body=[{req_body}.")

    resp = requests.post(
      url=f"{openapi_endpoint}", json=req_body, headers=req_headers,
      timeout=DEFAULT_TIMEOUT)

    if resp.status_code != 200:
      raise InternalServerError(
        f"Error status {resp.status_code}: {str(resp)}")

    json_response = resp.json()
    Logger.info(f"Got LLM service response {json_response}")
    output = json_response["choices"][0]["message"]["content"]
    return output

  aip_endpoint = f"projects/{PROJECT_ID}/locations/" \
                 f"{REGION}/endpoints/{aip_endpoint_name}"
  Logger.info(f"Generating text using Model Garden "
              f"endpoint=[{aip_endpoint}], prompt=[{prompt}], "
              f"parameters=[{parameters}.")

  if parameters is None:
    parameters = get_provider_value(PROVIDER_MODEL_GARDEN,
                                    KEY_MODEL_PARAMS, llm_type)

  parameters.update({"prompt": f"'{prompt}'"})

  instances = [parameters, ]
  endpoint_without_peft = google.cloud.aiplatform.Endpoint(aip_endpoint)

  response = await endpoint_without_peft.predict_async(instances=instances)

  predictions_text = "\n".join(response.predictions)
  Logger.info(f"Received response from "
              f"{response.model_resource_name} version="
              f"[{response.model_version_id}] with {len(response.predictions)}"
              f" prediction(s) = [{predictions_text}] ")

  return predictions_text

async def google_llm_predict(prompt: str, is_chat: bool, is_multimodal: bool,
                google_llm: str, user_chat: Optional[UserChat]=None,
                user_file_bytes: bytes=None,
                user_files: List[DataSourceFile]=None,
                stream: bool=False) -> Union[str, AsyncGenerator[str, None]]:
  """
  Generate text with a Google multimodal LLM given a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    is_chat: true if the model is a chat model
    is_multimodal: true if the model is a multimodal model
    google_llm: name of the vertex llm model
    user_chat: chat history
    user_file_bytes: the bytes of the file provided by the user
    user_files: list of DataSourceFiles for files provided by the user
    stream: whether to stream the response
  Returns:
    Either the full text response as str, or an AsyncGenerator yielding response chunks
  """

  user_file_bytes_log = user_file_bytes[:10] if user_file_bytes else None
  Logger.info(f"Generating text with a Google multimodal LLM:"
              f" prompt=[{prompt}], is_chat=[{is_chat}],"
              f" is_multimodal=[{is_multimodal}], google_llm=[{google_llm}],"
              f" user_file_bytes=[{user_file_bytes_log}],"
              f" user_files=[{user_files}]")

  # TODO: Consider images in chat
  prompt_list = []
  if user_chat is not None:
    history = user_chat.history
    for entry in history:
      content = UserChat.entry_content(entry)
      if UserChat.is_human(entry):
        prompt_list.append(f"Human input: {content}")
        prompt_list.append('here1')
      elif UserChat.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
        prompt_list.append('here2')
      elif is_multimodal:
        prompt_list.append('here3')
        if UserChat.is_file_bytes(entry):
          prompt_list.append('here4')
          prompt_list.append(
            Part.from_data(base64.b64decode(UserChat.get_file_b64(entry)),
                            mime_type=UserChat.get_file_type(entry)))
        elif UserChat.is_file_uri(entry):
          prompt_list.append(Part.from_uri(UserChat.get_file_uri(entry),
                                      mime_type=UserChat.get_file_type(entry)))
  prompt_list.append(prompt)
  # the context prompt is only used for non-gemini models and canot handle
  # the gemini Part object
  context_prompt = "\n\n".join(entry for entry in prompt_list
                               if isinstance(entry, str))

  # Get model params. If params are set at the model level
  # use those else use global vertex params.
  parameters = {}
  provider_config = get_provider_model_config(PROVIDER_VERTEX)
  for _, model_config in provider_config.items():
    model_name = model_config.get(KEY_MODEL_NAME)
    if model_name == google_llm and KEY_MODEL_PARAMS in model_config:
      parameters = model_config.get(KEY_MODEL_PARAMS)
  else:
    parameters = get_provider_value(PROVIDER_VERTEX,
                                    KEY_MODEL_PARAMS)

  try:
    if is_chat:
      # gemini uses new "GenerativeModel" class and requires different params
      if "gemini" in google_llm:
        # TODO: fix safety settings
        safety_settings = {
             HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
             HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
             HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
             HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        }
        chat_model = GenerativeModel(google_llm)
        if is_multimodal:
          if user_file_bytes is not None and user_files is not None:
            # user_file_bytes refers to a single image and so we index into
            # user_files (a list) to get a single mime type
            prompt_list.append(Part.from_data(user_file_bytes,
                                            mime_type=user_files[0].mime_type))
          elif user_files is not None:
            # user_files is a list referring to one or more images
            for user_file in user_files:
              prompt_list.append(Part.from_uri(user_file.gcs_path,
                                               mime_type=user_file.mime_type))
        Logger.info(f"context list {prompt_list}")
        generation_config = GenerationConfig(**parameters)
        response = await chat_model.generate_content_async(prompt_list,
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=stream)

        if stream:
          async def response_generator():
            try:
              async for chunk in response:
                if chunk.text:
                  yield chunk.text
            except ValueError as e:
              if "Cannot get the Candidate text." in str(e):
                candidate_info = ""
                candidate_start = str(e).find("Candidate:")
                if candidate_start != -1:
                  candidate_info = str(e)[candidate_start:]
                yield (
                  " \n ...I'm sorry, any further response has been blocked because the "
                  "succeeding content violates my safety filters.\n"
                  f"Details: {candidate_info}"
                )
                return
              else:
                raise
            except Exception as e:
              raise InternalServerError(str(e)) from e
          return response_generator()

        return response.text

      else:
        chat_model = ChatModel.from_pretrained(google_llm)
        chat = chat_model.start_chat()
        response = await chat.send_message_async(context_prompt, **parameters)
    else:
      text_model = TextGenerationModel.from_pretrained(google_llm)
      response = await text_model.predict_async(
          context_prompt,
          **parameters,
      )

  except Exception as e:
    raise InternalServerError(str(e)) from e

  Logger.info(f"Received response from the Model [{response.text}]")
  response = response.text

  return response
