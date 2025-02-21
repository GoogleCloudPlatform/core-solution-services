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

import { envOrFail } from "@/lib/env"
import { Chat, ChatModel, Query, QueryEngine, QueryEngineBuildJob } from "@/lib/types"
import axios from "axios"
import { path } from "ramda"

interface RunQueryParams {
  engine: string
  userInput: string
  llmType: string
  chatMode?: boolean
}

interface RunChatParams {
  userInput: string
  llmType: string
  uploadFile?: File
  fileUrl: string
  stream?: boolean
  toolNames?: string[]
  history?: Array<{ [key: string]: string }>
  temperature?: number
  queryEngineId?: string
  queryFilter?: Record<string, any>
}

interface ResumeQueryParams {
  queryId: string
  userInput: string
  llmType: string
  stream: boolean
  chatMode?: boolean
}

interface ResumeChatParams {
  chatId: string
  userInput: string
  llmType: string
  toolNames?: string[]
  stream?: boolean
  temperature?: number
  queryEngineId?: string
  queryFilter?: Record<string, any>
}

interface ResumeChatApiParams {
  prompt: string;
  llm_type: string;
  stream: boolean;
  tool_names?: string;
  temperature?: number;
  query_engine_id?: string;
  query_filter?: Record<string, any>;
}

interface JobStatusResponse {
  status: "success" | "failed" | "active"
}

interface UpdateChatParams {
  chatId: string
  title?: string
  history?: Array<{ [key: string]: string }>
}

interface ModelResponse {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
  date_added: string;
  is_multi: boolean;
  model_params?: {
    temperature?: number;
    [key: string]: any;
  };
}

const endpoint = envOrFail(
  "VITE_PUBLIC_API_ENDPOINT",
  import.meta.env.VITE_PUBLIC_API_ENDPOINT,
)

export const fetchAllChatModels =
  (token: string, isMultimodal?: boolean) => async (): Promise<ChatModel[] | undefined> => {
    let url = `${endpoint}/chat/chat_types/details`
    if (isMultimodal !== undefined) {
      url += `?is_multimodal=${isMultimodal}`
    }
    const headers = { Authorization: `Bearer ${token}` }

    try {
      const response = await axios.get(url, { headers });
      const modelDetails: ModelResponse[] = response.data.data;

      if (!modelDetails) return undefined;

      // Transform backend model details into ChatModel objects
      const chatModels: ChatModel[] = modelDetails.map((model: ModelResponse) => {
        // Calculate if model is new (added in last 30 days)
        const dateAdded = new Date(model.date_added);
        const now = new Date();
        const daysSinceAdded = Math.floor((now.getTime() - dateAdded.getTime()) / (1000 * 60 * 60 * 24));
        const isNew = daysSinceAdded <= 30;

        return {
          id: model.id,
          name: model.name,
          description: model.description,
          purposes: model.capabilities,
          isNew: isNew,
          isMultimodal: model.is_multi,
          modelParams: model.model_params
        };
      });

      return chatModels;
    } catch (error) {
      console.error('Error fetching chat models:', error);
      throw error;
    }
  };

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
    toolNames,
    stream = true,
    history,
    temperature,
    queryEngineId,
    queryFilter
  }: RunChatParams): Promise<Chat | ReadableStream | undefined | null> => {
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
    if (toolNames && toolNames.length > 0) {
      formData.append('tool_names', JSON.stringify(toolNames))
    }
    if (history) formData.append('history', JSON.stringify(history))
    if (temperature !== undefined) formData.append('temperature', String(temperature))
    if (queryEngineId) formData.append('query_engine_id', queryEngineId)
    if (queryFilter) formData.append('query_filter', JSON.stringify(queryFilter))

    if (stream) {
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          body: formData
        })

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message.replace(/^\d+\s+/, ''))
        }
        return response.body
      } catch (error: any) {
        console.error('Error in createChat:', error);
        throw error;
      }
    }

    return axios.post(url, formData, { headers }).then(path(["data", "data"]))
  }

export const fetchLatestChat = (token: string) => async (): Promise<Chat | null | undefined> => {
  try {
    const url = `${endpoint}/chat`; // Use the new endpoint
    const headers = { Authorization: `Bearer ${token}` };

    const response = await axios.get(url, { headers });
    const chatList = response.data.data; // Assuming your API returns data in a "data" field


    if (!chatList || chatList.length === 0) {
      return null; // Return null if no chats exist
    }


    // Sort the chat list by last_modified_time in descending order (newest first)
    const sortedChatList = [...chatList].sort((a, b) => (
      new Date(b.last_modified_time).getTime() - new Date(a.last_modified_time).getTime()
    ));

    const latestChatId = sortedChatList[0].id; // Get the ID of the latest chat


    if (!latestChatId) {
      return null; // Return null if the latest chat has no ID (shouldn't happen, but good to check)
    }

    // Fetch the latest chat details using the ID
    return fetchChat(token, latestChatId)();

  } catch (error) {
    console.error("Error fetching latest chat:", error);
    return null; // Return null if there's an error
  }
};

export const resumeChat =
  (token: string) => async ({
    chatId,
    userInput,
    llmType,
    toolNames,
    stream = true,
    temperature,
    queryEngineId,
    queryFilter
  }: ResumeChatParams): Promise<Chat | ReadableStream | undefined | null> => {
    const url = `${endpoint}/chat/${chatId}/generate`
    const headers = { Authorization: `Bearer ${token}` }
    let data: ResumeChatApiParams = {
      prompt: userInput,
      llm_type: llmType,
      stream
    }
    if (toolNames && toolNames.length > 0) {
      data['tool_names'] = JSON.stringify(toolNames)
    }
    if (temperature !== undefined) {
      data['temperature'] = temperature
    }
    if (queryEngineId) {
      data['query_engine_id'] = queryEngineId
    }
    if (queryFilter) {
      data['query_filter'] = queryFilter
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
          const errorData = await response.json();
          throw new Error(errorData.message.replace(/^\d+\s+/, ''))
        }
        return response.body
      } catch (error) {
        console.error('Error in resumeChat:', error);
        throw error;
      }
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

export const fetchEngine =
  (token: string, engineId: string | null) => (): Promise<QueryEngine | undefined | null> => {
    if (!engineId) return Promise.resolve(null)
    const url = `${endpoint}/query/engine/${engineId}`
    const headers = { Authorization: `Bearer ${token}` }
    return axios.get(url, { headers }).then(path(["data", "data"]))
  }


export const createQueryEngine =
  (token: string) => async (queryEngine: QueryEngine): Promise<QueryEngineBuildJob | undefined> => {
    const url = `${endpoint}/query/engine`;
    const headers = { Authorization: `Bearer ${token}` };

    const data = {
      query_engine: queryEngine.name,
      query_engine_type: queryEngine.query_engine_type,
      doc_url: queryEngine.doc_url,
      embedding_type: queryEngine.embedding_type,
      vector_store: queryEngine.vector_store,
      description: queryEngine.description,
      params: {
        depth_limit: queryEngine.depth_limit,
        agents: queryEngine.agents,
        associated_engines: queryEngine.child_engines,
        manifest_url: queryEngine.manifest_url,
        chunk_size: queryEngine.chunk_size,
        is_multimodal: queryEngine.is_multimodal ? "True" : "False",
      },
    };

    try {
      console.log("Making API request to:", url);
      console.log("Request headers:", headers);
      console.log("Request payload:", data);

      const response = await axios.post(url, data, { headers });

      console.log("API response:", response.data); // Debugging API response

      return response.data?.data; // Ensure correct parsing
    } catch (error: any) {
      console.error("API call failed:", error.response ? error.response.data : error.message);
      throw new Error(error.response?.data?.message || "Failed to create query engine");
    }
  };


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
    chatMode = true
  }: RunQueryParams): Promise<Chat | undefined> => {
    const url = `${endpoint}/query/engine/${engine}`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
      chat_mode: chatMode
    }
    const response = await axios.post(url, data, { headers })
    const responseData = response.data.data

    // Return Chat object if chat data exists
    if (responseData.user_chat) {
      return responseData.user_chat
    }
    
    // Otherwise return undefined
    return undefined
  }

export const resumeQuery =
  (token: string) => async ({
    queryId,
    userInput,
    llmType, 
    stream = false,
    chatMode = false
  }: ResumeQueryParams): Promise<Query | Chat | undefined> => {
    const url = `${endpoint}/query/${queryId}`
    const headers = { Authorization: `Bearer ${token}` }
    const data = {
      prompt: userInput,
      llm_type: llmType,
      sentence_references: false,
      stream,
      chat_mode: chatMode
    }

    try {
      const response = await axios.post(url, data, { headers })
      const responseData = response.data.data
      
      // Return Chat object if chat_mode is true and chat data exists
      if (chatMode && responseData.user_chat) {
        return responseData.user_chat
      }

      // Otherwise return Query ID
      return responseData.user_query_id
    } catch (error) {
      console.error('Error in resumeQuery:', error)
      throw error
    }
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

