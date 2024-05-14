"""
Serve LLAMA2 Model using truss
"""
from typing import Dict

import os
import torch
import urllib3
from transformers import pipeline, LlamaForCausalLM, LlamaTokenizer
from google.cloud import secretmanager

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secrets = secretmanager.SecretManagerServiceClient()

MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"
MAX_LENGTH = "1024"

DEFAULT_MAX_LENGTH_STR = os.getenv("DEFAULT_MAX_LENGTH")
if DEFAULT_MAX_LENGTH_STR is None or DEFAULT_MAX_LENGTH_STR == "":
    DEFAULT_MAX_LENGTH_STR = MAX_LENGTH
DEFAULT_MAX_LENGTH = int(DEFAULT_MAX_LENGTH_STR)

PROJECT_ID = os.environ.get("PROJECT_ID")
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
if HUGGINGFACE_API_KEY is None:
    try:
        print(f"Loading HuggingFace API Key from secret manager")
        HUGGINGFACE_API_KEY = secrets.access_secret_version(
            request={
                "name": "projects/" + PROJECT_ID +
                        "/secrets/huggingface-api-key/versions/latest"
            }).payload.data.decode("utf-8").strip()
    except Exception as exc:
        print(f"ERROR while loading huggingface_api_key: {exc}")
        HUGGINGFACE_API_KEY = None

assert HUGGINGFACE_API_KEY, "HUGGINGFACE_API_KEY is not set"
assert PROJECT_ID, "PROJECT_ID is not set"

print()
print("MODEL_NAME: ", MODEL_NAME)
print("DEFAULT_MAX_LENGTH: ", DEFAULT_MAX_LENGTH)
print("HUGGINGFACE_API_KEY: ", HUGGINGFACE_API_KEY)
print("PROJECT_ID: ", PROJECT_ID)
print()


class Model:
    def __init__(self, data_dir: str, config: Dict, **kwargs) -> None:
        self._tokenizer = None
        self._model = None
        self._data_dir = data_dir
        self._config = config
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print("THE DEVICE INFERENCE IS RUNNING ON IS: ", self.device)
        self.pipeline = None
        self._secrets = kwargs["secrets"]
        self.huggingface_api_token = HUGGINGFACE_API_KEY

    def load(self):

        self._model = LlamaForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf",
            token=self.huggingface_api_token,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self._tokenizer = LlamaTokenizer.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf",
            token=self.huggingface_api_token
        )

        print("Model Loaded.")

        self.pipeline = pipeline(
            "text-generation",
            model=self._model,
            tokenizer=self._tokenizer,
            torch_dtype=torch.bfloat16,
            trust_remote_code=True,
            device_map="auto",
        )

    def predict(self, request: Dict) -> Dict:
        with torch.no_grad():
            try:
                prompt = request.pop("prompt")
                max_length = request.pop("max_length", DEFAULT_MAX_LENGTH)
                print(f"Running prediction with prompt: {prompt}, "
                      f"max_length: {max_length}, {request}")
                data = self.pipeline(
                    prompt,
                    eos_token_id=self._tokenizer.eos_token_id,
                    max_length=max_length,
                    **request
                )[0]
                print(f"Prediction completed - {data}")
                return {"data": data}

            except Exception as exc:
                print(f"ERROR while running prediction: {exc}")
                return {"status": "error", "data": None, "message": str(exc)}
