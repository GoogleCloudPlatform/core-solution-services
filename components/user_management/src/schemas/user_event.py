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
Pydantic Model for UserEvent API's
"""
from typing import Optional, List
from pydantic import ConfigDict, BaseModel


class UserEventModel(BaseModel):
  """User Pydantic Model"""
  session_ref: Optional[str] = None
  raw_response: Optional[dict] = None
  feedback: Optional[dict] = None
  learning_item_id: str
  activity_type: str
  learning_unit: str
  course_id: str
  flow_type: str
  hint: Optional[str] = None
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "session_ref": "fjdsalfjaslf",
          "raw_response": {
              "first_attempt": "microanalytic theory"
          },
          "feedback": {
              "first_attempt": {
                  "feedback_text": "can be improved",
                  "evaluation_score": 0.4,
                  "evaluation_flag": "incorrect"
              }
          },
          "learning_item_id": "dfkjasfals",
          "activity_type": "choose_the_fact",
          "learning_unit": "sjfdjfalfd39",
          "course_id": "fjkadsfalsdfa",
          "flow_type": "Let AITutor Guide Me"
      }
  })


class UserEventWithParent(UserEventModel):
  user_id: Optional[str] = None
  id: str


class UserEventModelResponse(BaseModel):
  success: Optional[bool] = True
  message: Optional[str] = "Successfully created User Event"
  data: UserEventWithParent
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example":{
      "success": True,
      "message": "Successfully created the User Event",
      "data": {
      "raw_response" : {"first_attempt": "microanalytic theory"},
      "feedback": {
        "first_attempt": {
          "feedback_text": "can be improved",
          "evaluation_score":0.4,
          "evaluation_flag":"incorrect"
          }
        },
      "learning_item_id": "dfkjasfals",
      "activity_type": "choose_the_fact",
      "learning_unit": "sjfdjfalfd39",
      "user_id": "jfkdajetieqte",
      "course_id": "fjkadsfalsdfa",
      "flow_type": "Let AITutor Guide Me",
      "id": "fdjksafakdsf"
    }
  }
  })

class UpdateUserEventModel(BaseModel):
  """User Pydantic Model"""
  session_ref: Optional[str] = None
  raw_response: Optional[dict] = None
  feedback: Optional[dict] = None
  learning_item_id: Optional[str] = None
  activity_type: Optional[str] = None
  user_id: Optional[str] = None
  course_id: Optional[str] = None
  flow_type: Optional[str] = None
  hint: Optional[str] = None
  model_config = ConfigDict(from_attributes=True, extra="forbid", json_schema_extra={
      "example": {
      "session_ref": "fjdsalfjaslf",
      "raw_response" : {"first_attempt": "microanalytic theory"},
      "feedback": {
        "first_attempt": {
          "feedback_text": "can be improved",
          "evaluation_score":0.4,
          "evaluation_flag":"incorrect"
          }
      },
      "learning_item_id": "dfkjasfals",
      "activity_type": "choose_the_fact",
      "user_id": "dfkajkfjalk",
      "course_id": "fjkadsfalsdfa",
      "flow_type": "Let AITutor Guide Me"
      }
  })


class GetUserEvent(UserEventModelResponse):
  message: Optional[str] = "Successfully fetched User Event"
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example":{
      "success": True,
      "message": "Successfully fetched the User Event",
      "data": {
      "raw_response" : {"first_attempt": "microanalytic theory"},
      "feedback": {
        "first_attempt": {
          "feedback_text": "can be improved",
          "evaluation_score":0.4,
          "evaluation_flag":"incorrect"
        }
      },
      "learning_item_id": "dfkjasfals",
      "activity_type": "choose_the_fact",
      "learning_unit": "sjfdjfalfd39",
      "user_id": "jfkdajetieqte",
      "course_id": "fjkadsfalsdfa",
      "flow_type": "Let AITutor Guide Me",
      "id": "dsfalfjdasjlfk"
    }
    }
  })


class GetAllUserEvents(UserEventModelResponse):
  message: Optional[str] = "Successfully fetched all UserEvents"
  data: List[UserEventWithParent]
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
    "example":{
      "success": True,
      "message": "Successfully fetched the User Event",
      "data": [{
      "raw_response" : {"first_attempt": "microanalytic theory"},
      "feedback": {
        "first_attempt": {
          "feedback_text": "can be improved",
          "evaluation_score":0.4,
          "evaluation_flag":"incorrect"
        }
      },
      "learning_item_id": "dfkjasfals",
      "activity_type": "choose_the_fact",
      "learning_unit": "sjfdjfalfd39",
      "user_id": "jfkdajetieqte",
      "course_id": "fjkadsfalsdfa",
      "flow_type": "Let AITutor Guide Me",
      "id": "dfsafakljdfa"
    }]
    }
  })


class DeleteUserEvent(BaseModel):
  success: Optional[bool] = True
  message: Optional[str] = "Successfully deleted the User Event"
  model_config = ConfigDict(from_attributes=True, json_schema_extra={
      "example": {
          "success": True,
          "message": "Successfully deleted the User Event"
      }
  })
