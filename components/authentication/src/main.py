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
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import (refresh_token, validate_token, password, sign_in, sign_up)
from common.config import CORS_ALLOW_ORIGINS, PROJECT_ID
from common.utils.http_exceptions import add_exception_handlers
from common.utils.logging_handler import Logger
from common.monitoring.middleware import (
  RequestTrackingMiddleware,
  PrometheusMiddleware,
  create_metrics_router
)

Logger = Logger.get_logger(__file__)

# Basic API config
service_title = "Authentication"
service_path = "authentication"
version = "v1"

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Add instrumentation middleware
app.add_middleware(
  RequestTrackingMiddleware,
  project_id=PROJECT_ID,
  service_name="authentication-service",
  log_factory_reset=False
)
app.add_middleware(
  PrometheusMiddleware,
  service_name="authentication-service"
)

# Create metrics router
metrics_router = create_metrics_router()
app.include_router(metrics_router)

@app.get("/ping")
def health_check():
  """Health Check API
  
  Returns:
      dict: Status object with success message
  """
  return {
    "success": True,
    "message": "Successfully reached Authentication microservice",
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
  title="Authentication APIs",
  version="latest")

api.include_router(sign_up.router)
api.include_router(sign_in.router)
api.include_router(password.router)
api.include_router(refresh_token.router)
api.include_router(validate_token.router)

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
