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
  LLM Microservice
"""
# pylint: disable=pointless-string-statement
# pylint: disable=wrong-import-position
""" For Local Development
import sys
sys.path.append("../../../common/src")
import os
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
os.environ["GOOGLE_CLOUD_PROJECT"] = "fake-project"
"""
import config
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import llm, chat, query, agent, agent_plan
from common.utils.http_exceptions import add_exception_handlers
from common.utils.logging_handler import Logger
from common.utils.auth_service import validate_token
from common.config import CORS_ALLOW_ORIGINS, PROJECT_ID
from common.monitoring.middleware import (
  RequestTrackingMiddleware,
  PrometheusMiddleware,
  create_metrics_router
)
#debug
from common.utils.logging_handler import debug_context_vars
from common.monitoring.middleware import create_debug_router

# Basic API config
service_title = "LLM Service API's"
service_path = "llm-service"
version = "v1"

# Initialize logger
logger = Logger.get_logger(__file__)

app = FastAPI()

print("*** STARTUP: main.py initializing ***")
print("*** STARTUP: Checking context vars in main.py ***")
debug_context_vars()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add monitoring middleware
app.add_middleware(
  RequestTrackingMiddleware,
  project_id=PROJECT_ID,
  service_name="llm_service"
)
app.add_middleware(
  PrometheusMiddleware,
  service_name="llm_service"
)

metrics_router = create_metrics_router()

@app.get("/ping")
def health_check():
  """Health Check API

  Returns:
      dict: Status object with success message
  """
  return {
      "success": True,
      "message": "Successfully reached LLM Service",
      "data": {}
  }

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
    version="latest",
    # docs_url=None,
    # redoc_url=None,
    dependencies=[Depends(validate_token)]
    )

app.include_router(metrics_router)

#debug
debug_router = create_debug_router()
app.include_router(debug_router)

api.include_router(llm.router)
api.include_router(chat.router)
api.include_router(query.router)
api.include_router(agent.router)
api.include_router(agent_plan.router)

#debug
print("*** STARTUP: All middleware added, checking context vars again ***")
debug_context_vars()

add_exception_handlers(app)
add_exception_handlers(api)
app.mount(f"/{service_path}/api/{version}", api)

if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=int(config.PORT),
    log_level="debug",
    reload=True
  )
