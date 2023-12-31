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
"""Rules RESTful Microservice"""

import uvicorn
import config
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from common.utils.http_exceptions import add_exception_handlers
from common.utils.auth_service import validate_token

from routes import rules, rulesets

# Basic API config
service_title = "Rules Engine"
service_path = "rules-engine"
version = "v1"

# Init FastAPI app
app = FastAPI()


@app.get("/ping")
def health_check():
  return True


@app.get("/", response_class=HTMLResponse)
@app.get(f"/{service_path}", response_class=HTMLResponse)
@app.get(f"/{service_path}/", response_class=HTMLResponse)
def hello():
  return f"""
  You've reached the {service_title}. <br>
  See <a href='/{service_path}/api/{version}/docs'>API docs</a>
  """


api = FastAPI(
    title=service_title,
    version=version,
    dependencies=[Depends(validate_token)])

# Append Rules CRUD APIs to the app.
api.include_router(rules.router)
api.include_router(rulesets.router)

add_exception_handlers(app)
add_exception_handlers(api)
app.mount(f"/{service_path}/api/{version}", api)

if __name__ == "__main__":
  uvicorn.run(
      "main:app",
      host="0.0.0.0",
      port=int(config.PORT),
      log_level="info",
      reload=True)
