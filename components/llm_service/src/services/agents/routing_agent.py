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

""" Routing Agent """

from common.models import QueryEngine, User, UserChat
from common.models.agent import AgentCapability
from common.models.llm import CHAT_AI
from common.utils.logging_handler import Logger
from services.agents.agent_service import run_intent
from services.agents.db_agent import run_db_agent
from services.agents.agent_service import agent_plan, run_agent
from services.query.query_service import query_generate

Logger = Logger.get_logger(__file__)

async def run_routing_agent(prompt: str,
                            agent_name: str,
                            user: User,
                            user_chat: UserChat = None):

  # Get the intent based on prompt.
  route, route_logs = await run_intent(
      prompt, chat_history=user_chat.history)

  Logger.info(f"Intent chooses this best route: {route}, " \
              f"based on user prompt: {prompt}")
  Logger.info(f"Chosen route: {route}")

  route_parts = route.split(":", 1)
  route_type = route_parts[0]
  route_name = route
  agent_logs = None

  # Executing based on the best intent route.
  chat_history_entry = {
    "route": route_type,
    "route_name": route_name,
  }
  response_data = {
    "route": route_type,
    "route_name": route_name,
  }

  # Query Engine route
  if route_type == AgentCapability.AGENT_QUERY_CAPABILITY.value:
    # Run RAG via a specific query engine
    query_engine_name = route_parts[1]
    Logger.info("Dispatch to Query Engine: {query_engine_name}")

    query_engine = QueryEngine.find_by_name(query_engine_name)
    Logger.info("Query Engine: {query_engine}")

    if not llm_type:
      llm_type = query_engine.llm_type

    query_result, query_references = await query_generate(
          user.id,
          prompt,
          query_engine,
          llm_type,
          sentence_references=True)
    Logger.info(f"Query response="
                f"[{query_result}]")

    response_data = {
      "route": route_type,
      "route_name": f"Query Engine: {query_engine_name}",
      "output": query_result.response,
      "query_engine_id": query_result.query_engine_id,
      "query_references": query_references,
    }
    chat_history_entry = response_data
    chat_history_entry[CHAT_AI] = query_result.response

  # Database route
  elif route_type == AgentCapability.AGENT_DATABASE_CAPABILITY.value:
    # Run a query against a DB dataset. Return a dict of
    # "columns: column names, "data": row data
    dataset_name = route_parts[1]

    Logger.info("Dispatch to DB Query: {dataset_name}")

    db_result, agent_logs = await run_db_agent(
        prompt, llm_type, dataset_name, user.email)
    # Logger.info(f"DB query response: \n{db_result}")

    # TODO: Update with the output generated from the LLM.
    if db_result.get("data", None):
      response_output = "Here is the database query result in the attached " \
                        "resource."
    else:
      response_output = "Unable to find the query result from the database."

    response_data = {
      "route": route_type,
      "route_name": f"Database Query: {dataset_name}",
      f"{CHAT_AI}": response_output,
      "content": response_output,
      # "data": db_result["data"],
      "dataset": dataset_name,
      "resources": db_result["resources"],
      "agent_logs": agent_logs,
    }
    chat_history_entry = response_data

  # Plan route
  elif route_type == AgentCapability.AGENT_PLAN_CAPABILITY.value:
    # Run PlanAgent to generate a plan
    output, user_plan = await agent_plan(
        agent_name="Plan", prompt=prompt, user_id=user.id)
    plan_data = user_plan.get_fields(reformat_datetime=True)
    plan_data["id"] = user_plan.id
    chat_history_entry[CHAT_AI] = output
    chat_history_entry["plan"] = plan_data

    response_data = {
      "content": output,
      "plan": plan_data,
      "agent_logs": agent_logs,
    }

  # Anything else including Chat route.
  else:
    # Run with the generic ChatAgent for anything else.
    output = await run_agent("Chat", prompt)
    chat_history_entry[CHAT_AI] = output
    response_data = {
      "content": output,
    }

  # Appending Agent's thought process.
  if agent_logs:
    chat_history_entry["agent_logs"] = agent_logs
    response_data["agent_logs"] = agent_logs
  if route_logs:
    chat_history_entry["route_logs"] = route_logs
    response_data["route_logs"] = route_logs

  user_chat.update_history(custom_entry=chat_history_entry)
  user_chat.save()

  chat_data = user_chat.get_fields(reformat_datetime=True)
  chat_data["id"] = user_chat.id
  response_data["chat"] = chat_data
  response_data["route_name"] = route_name

  return route, response_data

