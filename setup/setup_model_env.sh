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

set -e

export ENABLE_LLAMA2CPP_LLM="True"
export ENABLE_GOOGLE_LLM="False"
export ENABLE_OPENAI_LLM="False"
export ENABLE_COHERE_LLM="False"
export ENABLE_TRUSS_LLAMA2="True"
export ENABLE_GOOGLE_MODEL_GARDEN="False"

# gs://genie-demo-gdch-llama2/llama-2-13b-chat_ggml-model-f16.gguf
# gs://genie-demo-gdch-llama2/llama-2-70b-chat_ggml-model-f16.gguf
# gs://genie-demo-gdch-llama2/llama-2-7b-chat_ggml-model-f16.gguf

# export LLAMA2CPP_MODEL_FILE="gs://"

echo
echo "SKAFFOLD_NAMESPACE=${SKAFFOLD_NAMESPACE}"
echo "PROJECT_ID=${PROJECT_ID}"
echo

echo "ENABLE_LLAMA2CPP_LLM=${ENABLE_LLAMA2CPP_LLM}"
echo "ENABLE_GOOGLE_LLM=${ENABLE_GOOGLE_LLM}"
echo "ENABLE_OPENAI_LLM=${ENABLE_OPENAI_LLM}"
echo "ENABLE_COHERE_LLM=${ENABLE_COHERE_LLM}"
echo "ENABLE_TRUSS_LLAMA2=${ENABLE_TRUSS_LLAMA2}"
echo "ENABLE_GOOGLE_MODEL_GARDEN=${ENABLE_GOOGLE_MODEL_GARDEN}"
