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

from common.config import PROJECT_ID, REGION
from common.models import UserChat
from common.utils.errors import ResourceNotFoundException
from common.utils.http_exceptions import InternalServerError
from common.utils.logging_handler import Logger
from common.utils.request_handler import post_method
from common.utils.token_handler import UserCredentials
from config import (get_model_config, get_provider_models,
                    get_provider_value,
                    PROVIDER_VERTEX, PROVIDER_TRUSS,
                    PROVIDER_MODEL_GARDEN,
                    KEY_MODEL_ENDPOINT, KEY_MODEL_NAME,
                    KEY_MODEL_PARAMS,
                    DEFAULT_LLM_TYPE, LANGCHAIN_LLM, GOOGLE_LLM,
                    GOOGLE_MODEL_GARDEN, LLM_SERVICE_MODELS,
                    LLM_TRUSS_MODELS
                    )
from services.langchain_service import langchain_llm_generate

Logger = Logger.get_logger(__file__)

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

    # for Google models, prioritize native client over langchain
    chat_llm_types = get_model_config().get_chat_llm_types()
    if llm_type in LLM_SERVICE_MODELS:
      is_chat = llm_type in chat_llm_types
      response = await llm_service_predict(prompt, is_chat, llm_type)
    elif llm_type in LLM_TRUSS_MODELS:
      model_endpoint = get_model_config().get_provider_value(
          PROVIDER_TRUSS, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_truss_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in GOOGLE_MODEL_GARDEN:
      aip_endpoint_name = get_model_config().get_provider_value(
          PROVIDER_MODEL_GARDEN, KEY_MODEL_ENDPOINT, llm_type)
      response = await model_garden_predict(prompt, aip_endpoint_name)
    elif llm_type in GOOGLE_LLM:
      google_llm = get_model_config().get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      is_chat = llm_type in chat_llm_types
      response = await google_llm_predict(prompt, is_chat, google_llm)
    elif llm_type in LANGCHAIN_LLM:
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
                   user_chat: Optional[UserChat] = None) -> str:
  """
  Send a prompt to a chat model and return response.
  Args:
    prompt: the text prompt to pass to the LLM
    llm_type: the type of LLM to use
    user_chat (optional): a user chat to use for context
  Returns:
    the text response: str
  """
  Logger.info(f"Generating chat with llm_type=[{llm_type}].")
  Logger.debug(f"prompt=[{prompt}].")
  if llm_type not in get_model_config().get_chat_llm_types():
    raise ResourceNotFoundException(f"Cannot find chat llm type '{llm_type}'")

  try:
    response = None

    if llm_type in LLM_SERVICE_MODELS:
      is_chat = True
      response = await llm_service_predict(prompt, is_chat, llm_type,
                                           user_chat)
    elif llm_type in LLM_TRUSS_MODELS:
      model_endpoint = get_model_config().get_provider_value(
          PROVIDER_TRUSS, KEY_MODEL_ENDPOINT, llm_type)
      response = await llm_truss_service_predict(
          llm_type, prompt, model_endpoint)
    elif llm_type in GOOGLE_MODEL_GARDEN:
      aip_endpoint_name = get_model_config().get_provider_value(
          PROVIDER_MODEL_GARDEN, KEY_MODEL_ENDPOINT, llm_type)
      response = await model_garden_predict(prompt, aip_endpoint_name)
    elif llm_type in GOOGLE_LLM:
      google_llm = get_model_config().get_provider_value(
          PROVIDER_VERTEX, KEY_MODEL_NAME, llm_type)
      is_chat = True
      response = await google_llm_predict(prompt, is_chat,
                                          google_llm, user_chat)
    elif llm_type in LANGCHAIN_LLM:
      response = await langchain_llm_generate(prompt, llm_type, user_chat)
    return response
  except Exception as e:
    raise InternalServerError(str(e)) from e

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
    parameters = get_model_config().get_provider_value(
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
  llm_service_config = LLM_SERVICE_MODELS.get(llm_type)
  if not auth_token:
    auth_client = UserCredentials(llm_service_config.get("user"),
                                  llm_service_config.get("password"))
    auth_token = auth_client.get_id_token()

  # start with base url of the LLM service we are calling
  api_url = llm_service_config.get("api_base_url")

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
                               aip_endpoint_name: str,
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
  aip_endpoint = f"projects/{PROJECT_ID}/locations/" \
                 f"{REGION}/endpoints/{aip_endpoint_name}"
  Logger.info(f"Generating text using Model Garden "
              f"endpoint=[{aip_endpoint}], prompt=[{prompt}], "
              f"parameters=[{parameters}.")

  if parameters is None:
    parameters = get_model_config().get_provider_value(PROVIDER_MODEL_GARDEN,
      KEY_MODEL_PARAMS)

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
  context_prompt = prompt.join("\n\n")

  # get global vertex model params
  parameters = get_model_config().get_provider_value(PROVIDER_VERTEX,
      KEY_MODEL_PARAMS)

  try:
    if is_chat:
      chat_model = ChatModel.from_pretrained(google_llm)
      chat = chat_model.start_chat(max_output_tokens=1024)
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
