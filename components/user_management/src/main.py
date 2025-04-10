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

"""
  User Management Service
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
import uvicorn
import config
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import (user_event, user, permission, action, user_group, staff,
                    module, session, application, association_group)
from common.utils.http_exceptions import add_exception_handlers
from common.utils.auth_service import validate_token
from common.utils.logging_handler import Logger
from common.config import CORS_ALLOW_ORIGINS, PROJECT_ID
from common.monitoring.middleware import (
  RequestTrackingMiddleware,
  PrometheusMiddleware,
  create_metrics_router
)

# Basic API config
service_title = "User Management Service"
service_path = "user-management"
version = "v1"

# Initialize logger
logger = Logger.get_logger(__file__)

# Create FastAPI app
app = FastAPI()

# Add CORS middleware if needed
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
  service_name="user-management-service",
  log_factory_reset=False
)
app.add_middleware(
  PrometheusMiddleware,
  service_name="user-management-service"
)

# Create metrics router
metrics_router = create_metrics_router()

@app.get("/ping")
def health_check() -> dict:
  """
  Endpoint to check the microservice health
  Params
  ------
  None
  Returns
  -------
  dict
  """
  return {
    "success": True,
    "message": "Successfully reached User Management Service",
    "data": {}
  }


add_exception_handlers(app)

# Create API v1 router
api = FastAPI(
  title="User Access Management Service APIs",
  version="latest",
  # docs_url=None,
  # redoc_url=None,
  dependencies=[Depends(validate_token)]
)

api.include_router(user.router)
api.include_router(user_group.router)
api.include_router(permission.router)
api.include_router(action.router)
api.include_router(module.router)
api.include_router(application.router)
api.include_router(session.router)
api.include_router(staff.router)
api.include_router(association_group.router)
add_exception_handlers(api)

# Create API v2 router
api_v2 = FastAPI(
  title="User Access Management Service APIs",
  version="latest",
  docs_url=None,
  redoc_url=None,
  dependencies=[Depends(validate_token)]
)

api_v2.include_router(user.router)
api_v2.include_router(user_event.router)

# Mount API router
app.mount(f"/{service_path}/api/{version}", api)

# Include metrics router
app.include_router(metrics_router)

if __name__ == "__main__":
  uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=int(config.PORT),
    log_level="debug",
    reload=True
  )
