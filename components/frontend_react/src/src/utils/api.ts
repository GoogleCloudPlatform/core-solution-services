// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the License);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { envOrFail } from "@/utils/env"
import { Chat, Query, QueryEngine, QueryEngineBuildJob } from "@/utils/types"
import axios from "axios"
import { path } from "ramda"

interface RunQueryParams {
  engine: string
  userInput: string
  llmType: string
}

interface RunChatParams {
  userInput: string
  llmType: string
}

interface ResumeQueryParams {
  queryId: string
  userInput: string
  llmType: string
}

interface ResumeChatParams {
  chatId: string
  userInput: string
  llmType: string
}

interface JobStatusResponse {
  status: "succeeded" | "failed" | "active"
}

const endpoint = envOrFail(
  "VITE_PUBLIC_API_ENDPOINT",
  import.meta.env.VITE_PUBLIC_API_ENDPOINT,
)

const jobsEndpoint = envOrFail(
  "VITE_PUBLIC_API_JOBS_ENDPOINT",
  import.meta.env.VITE_PUBLIC_API_JOBS_ENDPOINT,
)

export const fetchAllChatModels =
  (token: string) => (): Promise<string[] | undefined> => {
    const url = `${endpoint}/chat/chat_types`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
  }

export const fetchChatHistory =
  (token: string) => (): Promise<Chat[] | undefined> => {
    const params = new URLSearchParams({
      skip: "0",
      limit: "100",
    })
    const url = `${endpoint}/chat?${params.toString()}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
  }

export const fetchChat =
  (token: string, chatId: string | null) => (): Promise<Chat | undefined | null> => {
    if (!chatId) return Promise.resolve(null)
    const url = `${endpoint}/chat/${chatId}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
  }

export const createChat =
  (token: string) => async ({
    userInput,
    llmType,
  }: RunChatParams): Promise<Chat | undefined> => {
    const url = `${endpoint}/chat`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
    }
    return axios.post(url, data, { headers }).then(path(["data", "data"]))
  }

export const resumeChat =
  (token: string) => async ({
    chatId,
    userInput,
    llmType,
  }: ResumeChatParams): Promise<Chat | undefined> => {
    const url = `${endpoint}/chat/${chatId}/generate`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
    }
    return axios.post(url, data, { headers }).then(path(["data", "data"]))
  }

export const fetchQuery =
  (token: string, queryId: string | null) => (): Promise<Query | undefined | null> => {
    if (!queryId) return Promise.resolve(null)
    const url = `${endpoint}/query/${queryId}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
  }

export const fetchQueryHistory =
  (token: string) => (): Promise<Query[] | undefined> => {
    const params = new URLSearchParams({
      skip: "0",
      limit: "100",
    })
    const url = `${endpoint}/query/user?${params.toString()}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
  }

export const fetchAllEngines =
  (token: string) => (): Promise<QueryEngine[] | undefined> => {
    const url = `${endpoint}/query`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
  }

export const createQueryEngine =
  (token: string) => async (queryEngine: QueryEngine): Promise<QueryEngineBuildJob | undefined> => {
    const url = `${endpoint}/query/engine`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      "query_engine": queryEngine.name,
      "query_engine_type": queryEngine.query_engine_type,
      "doc_url": queryEngine.doc_url,
      "embedding_type": queryEngine.embedding_type,
      "vector_store": queryEngine.vector_store,
      "description": queryEngine.description,
      "params": {
        "depth_limit": queryEngine.depth_limit,
        "agents": queryEngine.agents,
        "associated_engines": queryEngine.child_engines,
      }
    }
    return axios.post(url, data, { headers }).then(path(["data", "data"]))
  }

export const updateQueryEngine =
  (token: string) => (queryEngine: QueryEngine): Promise<QueryEngine | undefined> => {
    const url = `${endpoint}/query/engine/${queryEngine.id}`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      "description": queryEngine.description,
    }
    return axios.put(url, data, { headers }).then(path(["data", "data"]))
  }

export const createQuery =
  (token: string) => async ({
    engine,
    userInput,
    llmType,
  }: RunQueryParams): Promise<Query | undefined> => {
    const url = `${endpoint}/query/engine/${engine}`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
    }
    return axios.post(url, data, { headers }).then(path(["data", "data", "user_query_id"]))
  }

export const resumeQuery =
  (token: string) => async ({
    queryId,
    userInput,
    llmType,
  }: ResumeQueryParams): Promise<Query | undefined> => {
    const url = `${endpoint}/query/${queryId}`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
      sentence_references: false,
    }
    return axios.post(url, data, { headers }).then(path(["data", "data", "user_query_id"]))
  }

export const getJobStatus =
  async (jobId: string, token: string): Promise<JobStatusResponse | undefined> => {
    if (!token) return Promise.resolve(undefined)
    const url = `${jobsEndpoint}/jobs/agent_run/${jobId}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
 }

export const getEngineJobStatus =
  async (jobId: string, token: string): Promise<JobStatusResponse | undefined> => {
    if (!token) return Promise.resolve(undefined)
    const url = `${jobsEndpoint}/jobs/query_engine_build/${jobId}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
 }

export const fetchAllEngineJobs =
  (token: string) => (): Promise<QueryEngineBuildJob[] | undefined> => {
    const url = `${jobsEndpoint}/jobs/query_engine_build`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
 }

