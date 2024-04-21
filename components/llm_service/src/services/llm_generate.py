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
# pylint: disable=import-outside-toplevel
import time
from typing import Optional
import google.cloud.aiplatform
from vertexai.preview.language_models import (ChatModel, TextGenerationModel)
from vertexai.preview.generative_models import GenerativeModel
from vertexai.preview.generative_models import (
    HarmCategory,
    HarmBlockThreshold)
from google.cloud.aiplatform_v1beta1.types.content import SafetySetting
from common.config import PROJECT_ID, REGION
from common.models import UserChat, UserQuery
from common.utils.errors import ResourceNotFoundException
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import post_method
from common.utils.token_handler import UserCredentials
from config import (get_model_config, get_provider_models,
                    get_provider_value, get_provider_model_config,
                    get_model_config_value,
                    PROVIDER_VERTEX, PROVIDER_TRUSS,
                    PROVIDER_MODEL_GARDEN,
                    PROVIDER_LANGCHAIN, PROVIDER_LLM_SERVICE,
                    KEY_MODEL_ENDPOINT, KEY_MODEL_NAME,
                    KEY_MODEL_PARAMS, KEY_MODEL_CONTEXT_LENGTH,
                    DEFAULT_LLM_TYPE)
from services.langchain_service import langchain_llm_generate
from utils.errors import ContextWindowExceededException

Logger = Logger.get_logger(__file__)

# A conservative characters-per-token constant, used to check
# whether prompt length exceeds context window size
CHARS_PER_TOKEN = 3

async def llm_generate(prompt: str, llm_type: str) -> str:
  """
  Generate text with an LLM given a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use (default to openai)
  Returns:
    the text response: str
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
    elif llm_type in get_provider_models(PROVIDER_MODEL_GARDEN):
      response = await model_garden_predict(prompt, llm_type)
    elif llm_type in get_provider_models(PROVIDER_VERTEX):
      google_llm = get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      if google_llm is None:
        raise RuntimeError(
            f"Vertex model name not found for llm type {llm_type}")
      is_chat = llm_type in chat_llm_types
      response = await google_llm_predict(prompt, is_chat, google_llm)
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

async def llm_chat(prompt: str, llm_type: str,
                   user_chat: Optional[UserChat] = None,
                   user_query: Optional[UserChat] = None) -> str:
  """
  Send a prompt to a chat model and return response.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use
    user_chat (optional): a user chat to use for context
    user_query (optional): a user query to use for context
  Returns:
    the text response: str
  """
  Logger.info(f"Generating chat with llm_type=[{llm_type}].")
  Logger.debug(f"prompt=[{prompt}].")
  if llm_type not in get_model_config().get_chat_llm_types():
    raise ResourceNotFoundException(f"Cannot find chat llm type '{llm_type}'")

  try:
    response = None

    # add chat history to prompt if necessary
    if user_chat is not None or user_query is not None:
      context_prompt = get_context_prompt(
          user_chat=user_chat, user_query=user_query)
      prompt = context_prompt + "\n" + prompt

    # check whether the context length exceeds the limit for the model
    check_context_length(prompt, llm_type)

    # call the appropriate provider to generate the chat response
    if llm_type in get_provider_models(PROVIDER_LLM_SERVICE):
      is_chat = True
      response = await llm_service_predict(prompt, is_chat, llm_type,
                                           user_chat)
    elif llm_type in get_provider_models(PROVIDER_TRUSS):
      model_endpoint = get_provider_value(
          PROVIDER_TRUSS, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_truss_service_predict(
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
      response = await google_llm_predict(prompt, is_chat,
                                          google_llm, user_chat)
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

  if user_query is not None:
    history = user_query.history
    for entry in history:
      content = UserQuery.entry_content(entry)
      if UserQuery.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserQuery.is_ai(entry):
        prompt_list.append(f"AI response: {content}")

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
  output = output.replace(prompt, "")
  # Llama 2 often adds quotes
  if output.startswith('"') or output.startswith("'"):
    output = output[1:]
  if output.endswith('"') or output.endswith("'"):
    output = output[:-1]

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
    aip_endpoint_name: endpoint id from the Vertex AI online predictions
    parameters (optional):  parameters to be used for prediction
  Returns:
    the prediction text.
  """
  aip_endpoint_name = get_provider_value(
      PROVIDER_MODEL_GARDEN, KEY_MODEL_ENDPOINT, llm_type)

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


async def google_llm_predict(prompt: str, is_chat: bool,
                             google_llm: str, user_chat=None) -> str:
  """
  Generate text with a Google LLM given a prompt.
  Args:
    prompt: the text prompt to pass to the LLM
    is_chat: true if the model is a chat model
    google_llm: name of the vertex llm model
    user_chat: chat history
  Returns:
    the text response.
  """
  Logger.info(f"Generating text with a Google LLM given a prompt,"
              f" is_chat=[{is_chat}], google_llm=[{google_llm}]")
  Logger.debug(f"prompt=[{prompt}].")
  prompt_list = []
  if user_chat is not None:
    history = user_chat.history
    for entry in history:
      content = UserChat.entry_content(entry)
      if UserChat.is_human(entry):
        prompt_list.append(f"Human input: {content}")
      elif UserChat.is_ai(entry):
        prompt_list.append(f"AI response: {content}")
  prompt_list.append(prompt)
  context_prompt = "\n\n".join(prompt_list)

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
        chat_model = GenerativeModel(google_llm)
        chat = chat_model.start_chat()
        safety_settings = [
             SafetySetting(
                 category=HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                 threshold=HarmBlockThreshold.BLOCK_NONE,
             ),
             SafetySetting(
                 category=HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                 threshold=HarmBlockThreshold.BLOCK_NONE,
             ),
             SafetySetting(
                 category=HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                 threshold=HarmBlockThreshold.BLOCK_NONE,
             ),
             SafetySetting(
                 category=HarmCategory.HARM_CATEGORY_HARASSMENT,
                 threshold=HarmBlockThreshold.BLOCK_NONE,
             ),
        ]
        response = await chat.send_message_async(context_prompt,
            generation_config=parameters, safety_settings=safety_settings)
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
