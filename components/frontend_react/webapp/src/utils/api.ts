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
  uploadFile: File
  fileUrl: string
  stream?: boolean
  history?: Array<{[key: string]: string}>
}

interface ResumeQueryParams {
  queryId: string
  userInput: string
  llmType: string
  stream: boolean
}

interface ResumeChatParams {
  chatId: string
  userInput: string
  llmType: string
  stream?: boolean
}

interface JobStatusResponse {
  status: "succeeded" | "failed" | "active"
}

interface UpdateChatParams {
  chatId: string
  title?: string
  history?: Array<{[key: string]: string}>
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
  (token: string, isMultimodal?: boolean) => (): Promise<string[] | undefined> => {
    let url = `${endpoint}/chat/chat_types`
    if (isMultimodal !== undefined) {
      url += `?is_multimodal=${isMultimodal}`
    }
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
    uploadFile,
    fileUrl,
    stream = true,
    history
  }: RunChatParams): Promise<Chat | ReadableStream | undefined> => {
    const url = `${endpoint}/chat`
    const headers = { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'multipart/form-data'
    }
    const formData = new FormData()
    formData.append('prompt', userInput)
    formData.append('llm_type', llmType)
    formData.append('stream', String(stream))
    if (uploadFile) formData.append('chat_file', uploadFile)
    if (fileUrl) formData.append('chat_file_url', fileUrl)
    if (history) formData.append('history', JSON.stringify(history))

    if (stream) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.body
      } catch (error) {
        console.error('Error in createChat:', error);
        throw error;
      }
    }

    return axios.post(url, formData, { headers }).then(path(["data", "data"]))
  }

export const resumeChat =
  (token: string) => async ({
    chatId,
    userInput,
    llmType,
    stream = true
  }: ResumeChatParams): Promise<Chat | ReadableStream | undefined> => {
    const url = `${endpoint}/chat/${chatId}/generate`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
      stream
    }

    if (stream) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { 
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(data)
        })

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.body
      } catch (error) {
        console.error('Error in resumeChat:', error);
        throw error;
      }
    }

    return axios.post(url, data, { headers }).then(path(["data", "data"]))
  }

export const fetchEmbeddingTypes =
  (token: string, are_multimodal: boolean) => (): Promise<string[] | undefined | null> => {
    let url = `${endpoint}/llm/embedding_types?is_multimodal=${are_multimodal}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
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

export const fetchEngine =
  (token: string, engineId: string | null) => (): Promise<QueryEngine | undefined | null> => {
    if (!engineId) return Promise.resolve(null)
    const url = `${endpoint}/query/engine/${engineId}`
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
        "manifest_url": queryEngine.manifest_url,
        "chunk_size": queryEngine.chunk_size,
        "is_multimodal": queryEngine.is_multimodal ? "True" : "False",
      }
    }
    return axios.post(url, data, { headers }).then(path(["data", "data"]))
  }

export const updateQueryEngine =
  (token: string) => async (queryEngine: QueryEngine): Promise<QueryEngine | undefined> => {
    const url = `${endpoint}/query/engine/${queryEngine.id}`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      "description": queryEngine.description,
    }
    return axios.put(url, data, { headers }).then(path(["data", "data"]))
  }

export const deleteQueryEngine =
  (token: string) => async (queryEngine: QueryEngine): Promise<boolean | undefined> => {
    const url = `${endpoint}/query/engine/${queryEngine.id}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.delete(url, { headers }).then(path(["data", "success"]))
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
    stream = false
  }: ResumeQueryParams): Promise<Query | undefined> => {
    const url = `${endpoint}/query/${queryId}`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
      sentence_references: false,
      stream
    }

    try {
      const response = await axios.post(url, data, { headers });
      return path(["data", "data", "user_query_id"], response);
    } catch (error) {
      console.error('Error in resumeQuery:', error);
      throw error;
    }
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

export const updateChat = 
  (token: string) => async ({
    chatId,
    title,
    history
  }: UpdateChatParams): Promise<Chat | undefined> => {
    const url = `${endpoint}/chat/${chatId}`
    const headers = { 
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
    const data = {
      ...(title && { title }),
      ...(history && { history })
    }
    return axios.put(url, data, { headers }).then(path(["data", "data"]))
  }

