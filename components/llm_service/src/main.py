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
from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import llm, chat, query, agent, agent_plan
from common.utils.http_exceptions import add_exception_handlers
from common.utils.logging_handler import Logger
from common.utils.auth_service import validate_token
from common.config import CORS_ALLOW_ORIGINS, PROJECT_ID
from starlette.middleware.base import BaseHTTPMiddleware
from metrics import PrometheusMiddleware, create_metrics_router
import uuid
import time
import logging

# Basic API config
service_title = "LLM Service API's"
service_path = "llm-service"
version = "v1"

Logger = Logger.get_logger(__file__)

class RequestTrackingMiddleware(BaseHTTPMiddleware):
  """Middleware to inject request_id and trace into logs."""
  async def dispatch(self, request: Request, call_next):
    request_id = request.headers.get("X-Request-ID")
    if not request_id:
      request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    request.state.start_time = time.time()
    trace = f"projects/{PROJECT_ID}/traces/{request_id}"
    request.state.trace = trace

    # Create a custom log record factory to inject request_id and trace
    original_factory = logging.getLogRecordFactory()

    def custom_log_record_factory(*args, **kwargs):
      record = original_factory(*args, **kwargs)
      record.request_id = request.state.request_id
      record.trace = request.state.trace
      return record

    logging.setLogRecordFactory(custom_log_record_factory)

    response = await call_next(request)
    # Restore original factory
    # logging.setLogRecordFactory(original_factory)

    response.headers["X-Request-ID"] = request_id
    return response

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestTrackingMiddleware)
app.add_middleware(PrometheusMiddleware)

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
api.include_router(llm.router)
api.include_router(chat.router)
api.include_router(query.router)
api.include_router(agent.router)
api.include_router(agent_plan.router)


add_exception_handlers(app)
add_exception_handlers(api)
app.mount(f"/{service_path}/api/{version}", api)

if __name__ == "__main__":
  uvicorn.run(
      "main:app",
      host="0.0.0.0",
      port=int(config.PORT),
      log_level="debug",
      reload=True)
