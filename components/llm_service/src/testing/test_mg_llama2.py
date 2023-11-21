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

""" Utility to run locally predictions using model garden  end points """
# pylint: disable=wrong-import-position
import asyncio
import os
import sys
from google.cloud import aiplatform_v1

sys.path.append(os.path.join(os.path.dirname(__file__), "../../../common/src"))
from services.llm_generate import model_garden_predict


PROJECT_ID = "gcp-mira-demo"
REGION = "us-central1"

os.environ["PROJECT_ID"] = PROJECT_ID
os.environ["REGION"] = REGION

# Endpoint ID from Online Prediction/vertex AI page
os.environ["MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID"] = "3894402015861669888"

client = aiplatform_v1.EndpointServiceClient()
prompt = "What is a Medicaid?"


async def test_model_garden_predict():
  parameters = {
      "max_tokens": 300,
      "temperature": 0.2,
      "top_p": 1.0,
      "top_k": 10,
  }
  #await llm_generate(prompt, "VertexAI-ModelGarden-LLAMA2-Chat")

  response = await model_garden_predict(aip_endpoint_name=os.environ
                                      ["MODEL_GARDEN_LLAMA2_CHAT_ENDPOINT_ID"],
                                        prompt=prompt,
                                        parameters=parameters)
  print(response)


if __name__ == "__main__":

  loop = asyncio.get_event_loop()
  try:
    asyncio.ensure_future(test_model_garden_predict())
    loop.run_forever()
  except KeyboardInterrupt:
    pass
  finally:
    loop.close()
