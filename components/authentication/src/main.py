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

"""Authentication Microservice"""
import config
import uvicorn
from fastapi import FastAPI
from routes import (refresh_token, validate_token, password, sign_in, sign_up,
                    inspace_token)
from common.utils.http_exceptions import add_exception_handlers

app = FastAPI()

"""
For Local Development
import sys
sys.path.append("../../../common/src")
import os
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
"""


@app.get("/ping")
def health_check():
  return {
    "success": True,
    "message": "Successfully reached Authentication microservice",
    "data": {}
  }

api = FastAPI(
  title="Authentication APIs",
  version="latest")
  # docs_url=None,
  # redoc_url=None)

api.include_router(sign_up.router)
api.include_router(sign_in.router)
api.include_router(password.router)
api.include_router(refresh_token.router)
api.include_router(validate_token.router)
api.include_router(inspace_token.router)

app.mount("/authentication/api/v1", api)

add_exception_handlers(app)
add_exception_handlers(api)

if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=int(config.PORT),
    log_level="debug",
    reload=config.IS_DEVELOPMENT)
