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
from typing import List, Tuple, Dict
from langchain.agents import AgentExecutor
from langchain.chains.router.llm_router import LLMRouterChain,RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE
from langchain.prompts import PromptTemplate
from common.models import QueryEngine, User, UserChat, BatchJobModel, JobStatus
from common.models.agent import AgentCapability
from common.models.llm import CHAT_AI
from common.utils.logging_handler import Logger
from config import get_agent_config
from services.agents.db_agent import run_db_agent
from services.agents.agents import BaseAgent
from services.agents.agent_service import (
    agent_plan,
    parse_action_output,
    parse_plan_step,
    run_agent)
from services.agents.utils import agent_executor_arun_with_logs
from services.query.query_service import query_generate
from services import langchain_service

Logger = Logger.get_logger(__file__)
DEFAULT_ROUTE = "Chat"

async def run_routing_agent(prompt: str,
                            agent_name: str,
                            user: User,
                            user_chat: UserChat,
                            llm_type: str = None,
                            route: str = None,
                            db_result_limit: int = 10) -> Tuple[str, dict]:
  """
  Determine intent from user prompt for best route to fulfill user
  input.  Then execute that route.
  Args:
    prompt: user prompt
    agent_name: routing agent name.  "default": use the first routing agent
    user: User model for user making request
    user_chat: optional existing user chat object for previous chat history
    llm_type: optional llm_type to use for agents, otherwise llm_type of
      routing agent is used
    route: predefined route. If non-empty, it will bypass the run_intent.
  Returns:
    tuple of route (AgentCapability value), response data dict
  """

  # Get the intent based on prompt by running intent agent
  if not route:
    route, route_logs = await run_intent(
        agent_name, prompt, chat_history=user_chat.history)

    Logger.info(f"Intent chooses this best route: {route}, "
                f"based on user prompt: {prompt}")
    Logger.info(f"Chosen route: {route}")
    assert route is not None

    # create default chat_history_entry
    user_chat.update_history(custom_entry={
      "route": route.split(":", 1)[0],
      "route_name": route,
      "route_logs": route_logs,
    })

  route_parts = route.split(":", 1)
  route_type = route_parts[0]
  agent_logs = None
  chat_history_entry = {}

  # get routing agent model
  routing_agent_config = get_agent_config()[agent_name]
  if not routing_agent_config:
    raise RuntimeError(f"Cannot find {agent_name}")

  # llm_type can be passed as an argument
  # otherwise llm_type is whatever is set for routing agent
  if llm_type is None:
    llm_type = routing_agent_config["llm_type"]
  if not llm_type:
    raise RuntimeError("Agent {agent_name} does not have llm_type set.")

  # Query Engine route
  if route_type == AgentCapability.QUERY.value:
    # Run RAG via a specific query engine
    query_engine_name = route_parts[1]
    Logger.info("Dispatch to Query Engine: {query_engine_name}")

    query_engine = QueryEngine.find_by_name(query_engine_name)
    Logger.info("Query Engine: {query_engine}")

    query_result, query_references = await query_generate(
        user.id,
        prompt,
        query_engine,
        llm_type,
        sentence_references=True)
    Logger.info(f"Query response="
                f"[{query_result}]")

    response_data = {
      "output": query_result.response,
      "query_engine_id": query_result.query_engine_id,
      "query_references": query_references,
    }
    chat_history_entry = response_data
    chat_history_entry[CHAT_AI] = query_result.response

  # Database route
  elif route_type == AgentCapability.DATABASE.value:
    # Run a query against a DB dataset. Return a dict of
    # "columns: column names, "data": row data
    dataset_name = route_parts[1]

    Logger.info(f"Dispatch to DB Query: {dataset_name}")

    db_result, agent_logs = await run_db_agent(
        prompt, llm_type, dataset_name, user.email)

    if "error" not in db_result:
      Logger.info(f"db_result: {db_result}")

      db_result_data = db_result.get("data", None)
      db_result_output = None
      if db_result_data:
        response_output = "Here is the database query result in the attached " \
                          "resource."
        db_result_output = []
        db_result_columns = db_result_data["columns"]
        Logger.info(f"db_result columns: {db_result_columns}")

        # Convert db_result data, from list of tuple to list of dicts.
        for row_entry in db_result_data["rows"]:
          row_entry = list(row_entry)
          row_dict = {}
          for index, column in enumerate(db_result_columns):
            row_dict[column] = row_entry[index]
          db_result_output.append(row_dict)

          if len(db_result_output) > db_result_limit:
            break
      else:
        response_output = "Unable to find the query result from the database."

    else:
      # Error in the db_agent's return.
      response_output = db_result["error"]
      db_result_output = []

    response_data = {
      f"{CHAT_AI}": response_output,
      "content": response_output,
      "db_result": db_result_output,
      "dataset": dataset_name,
      "resources": db_result["resources"],
    }
    chat_history_entry = response_data

  # Plan route
  elif route_type == AgentCapability.PLAN.value:
    # Run PlanAgent to generate a plan
    output, user_plan = await agent_plan(
        agent_name="Plan", prompt=prompt, user_id=user.id)
    plan_data = user_plan.get_fields(reformat_datetime=True)
    plan_data["id"] = user_plan.id
    chat_history_entry[CHAT_AI] = output
    chat_history_entry["plan"] = plan_data
    agent_logs = output

    response_data = {
      "content": output,
      "plan": plan_data,
    }

  # Anything else including Chat route.
  else:
    # Run with the generic ChatAgent for anything else.
    output = await run_agent("Chat", prompt)
    chat_history_entry[CHAT_AI] = output
    response_data = {
      "content": output
    }

  # Appending Agent's thought process.
  if agent_logs:
    chat_history_entry["agent_logs"] = agent_logs
    response_data["agent_logs"] = agent_logs

  # update chat data in response
  user_chat.update_history(custom_entry=chat_history_entry)
  user_chat.save()
  chat_data = user_chat.get_fields(reformat_datetime=True)
  chat_data["id"] = user_chat.id
  response_data["chat"] = chat_data
  response_data["route"] = route_type
  response_data["route_name"] = route

  Logger.info(f"Dispatch agent {agent_name} response: "
              f"route [{route}] response {response_data}")

  return route, response_data


async def run_intent(
        agent_name: str, prompt: str, chat_history: List = None,
        use_router_chain: bool = True) -> dict:
  """
  Evaluate a prompt to get the intent with best matched route.

  Args:
      prompt(str): the user input prompt
      agent_name(str): the name of the routing agent, or "default" to
                       use the first in the list
      chat_history(List): any previous chat history for context

  Returns:
      output(str): the output of the agent on the user input
      action_steps: the list of action steps take by the agent for the run
  """

  Logger.info(f"Running dispatch "
              f"with prompt=[{prompt}] and "
              f"chat_history=[{chat_history}]")

  # check for default routing agent
  if agent_name == "default":
    routing_agents = BaseAgent.get_agents_by_capability(
      AgentCapability.ROUTE.value
    )
    agent_name = routing_agents.keys()[0]

  # get llm service routing agent
  llm_service_agent = BaseAgent.get_llm_service_agent(agent_name)
  routing_agent_config = get_agent_config()[agent_name]

  # load corresponding langchain agent and instantiate agent_executor
  langchain_agent = llm_service_agent.load_langchain_agent()
  intent_agent_tools = llm_service_agent.get_tools()
  Logger.info(f"Routing agent tools [{intent_agent_tools}]")

  # Get all route options.
  route_list = get_route_list(llm_service_agent)
  Logger.info(f"route_list: {route_list}")
  agent_logs = None

  if use_router_chain:
    Logger.info("Evaluating intent using RouterChain")

    llm = langchain_service.get_model(routing_agent_config["llm_type"])
    router_chain = generate_router_chain(llm, route_list)
    result = router_chain.route(inputs ={
      "input": prompt,
      "verbose": True
    })
    Logger.info(f"RouterChain result: {result}")
    route = result.destination

  else:
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=langchain_agent, tools=intent_agent_tools)

    # get dispatch prompt
    dispatch_prompt = get_dispatch_prompt(route_list)

    agent_inputs = {
      "input": dispatch_prompt + prompt,
      "chat_history": []
    }

    Logger.info("Running agent executor to get best matched route.... ")
    output, agent_logs = await agent_executor_arun_with_logs(
        agent_executor, agent_inputs)

    Logger.info(f"Agent {agent_name} generated output=[{output}]")
    Logger.info(f"run_intent - agent_logs: \n{agent_logs}")
    routes = parse_action_output("Route:", output) or []

    Logger.info(f"Output routes: {routes}")

    # If no best route(s) found, pass to Chat agent.
    if not routes or len(routes) == 0:
      return AgentCapability.CHAT.value, agent_logs

    # TODO: Refactor this with RoutingAgentOutputParser
    # Get the route for the best matched (first) returned routes.
    route, detail = parse_plan_step(routes[0])[0]
    Logger.info(f"route: {route}, {detail}")

  # If no route found, use default Chat route.
  if not route:
    route = DEFAULT_ROUTE

  return route, agent_logs

def get_route_list(llm_service_agent: BaseAgent) -> list:
  agent_name = llm_service_agent.name
  route_list = [
    {
      "name": f"{AgentCapability.CHAT.value}",
      "description": "to to perform generic chat conversation.",
    },
    {
      "name": f"{AgentCapability.PLAN.value}",
      "description": " to compose, generate or create a plan.",
    }
  ]

  # Adding query engines to route list.
  query_engines = llm_service_agent.get_query_engines(agent_name)
  for qe in query_engines:
    route_list.append({
      "name": f"{AgentCapability.QUERY.value}:{qe.name}",
      "description": \
        f" to run a query on a search engine for information (not raw data)" \
        f" on the topics of {qe.description} \n"
    })

  # get datasets for this with their descriptions as topics
  datasets = llm_service_agent.get_datasets(agent_name)
  for ds_name, ds_config in datasets.items():
    description = ds_config["description"]
    route_list.append({
      "name": f"{AgentCapability.DATABASE.value}:{ds_name}",
      "description": \
        f" to use SQL to retrieve rows of data from a database for data " \
        f"related to these areas: {description} \n"
    })

  return route_list

def get_dispatch_prompt(route_list) -> str:
  """ Construct dispatch prompt for intent agent """

  route_list_str = ""
  for route in route_list:
    route_list_str += f" - [{route['name']}] {route['description']}\n"

  dispatch_prompt = \
      "The AI Routing Assistant has access to the following routes " + \
      "for a user prompt:\n" + \
      f"{route_list_str}\n" + \
      "Choose one route based on the question below:\n"
  Logger.info(f"dispatch_prompt: \n{dispatch_prompt}")

  return dispatch_prompt


async def batch_run_dispatch(request_body: Dict, job: BatchJobModel) -> Dict:
  # execute routing agent
  prompt = request_body["prompt"]
  agent_name = request_body["agent_name"]
  user_id = request_body["user_id"]
  chat_id = request_body["chat_id"]
  llm_type = request_body["llm_type"]
  db_result_limit = request_body.get("db_result_limit")
  route = request_body.get("route", None)

  user = User.find_by_id(user_id)
  user_chat = UserChat.find_by_id(chat_id)
  user_chat.update_history(custom_entry={
    "batch_job": {
      "job_id": job.id,
      "job_name": job.name,
    },
  })
  user_chat.save()

  route, response_data = await run_routing_agent(
      prompt, agent_name, user, user_chat, llm_type,
      db_result_limit=db_result_limit, route=route)

  job.message = f"Successfully ran dispatch with route: {route}"
  job.result_data = response_data
  job.status = JobStatus.JOB_STATUS_SUCCEEDED.value
  job.save()


def generate_router_chain(llm, route_list):
  """
  Generates the router chains from the prompt infos.
  :param route_list The prompt information generated above.
  """
  destinations = [
      f"{route['name']}: {route['description']}" for route in route_list]
  destinations_str = "\n".join(destinations)
  router_template = MULTI_PROMPT_ROUTER_TEMPLATE.format(
      destinations=destinations_str)
  router_prompt = PromptTemplate(
      template=router_template,
      input_variables=["input"],
      output_parser=RouterOutputParser()
  )
  router_chain = LLMRouterChain.from_llm(llm, router_prompt)
  return router_chain
