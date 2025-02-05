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

import { ReactNode } from "react"
import { z } from "zod"

export type INavigationItem = {
  name: string
  href: string
  show: () => boolean
  icon?: ReactNode
}

export type Theme = "light" | "dark"

export type IAuthProvider = "google" | "password"

export type IAppConfig = {
  siteName: string
  locale: string
  logoPath: string
  simpleLogoPath: string
  imagesPath: string
  theme: string
  authProviders: IAuthProvider[]
  authorizedDomains: RegExp[]
}

export const User = z.object({
  firstName: z.string(),
  lastName: z.string(),
})

export type IUser = z.infer<typeof User>

export const Users = z.array(User)

const FIELD_TYPE = [
  "string",
  "number",
  "bool",
  "select",
  "list(string)",
  "file",
  "file(upload)"
] as const

const FIELD_TYPE_ENUM = z.enum(FIELD_TYPE)

export const FormVariable = z.object({
  name: z.string(),
  display: z.string(),
  type: FIELD_TYPE_ENUM,
  description: z.string(),
  default: z.any().optional(),
  required: z.boolean(),
  group: z.union([z.number(), z.string()]),
  order: z.number().optional(),
  options: z.string().array().optional(),
  tooltip: z.string().optional(),
  fileLabel: z.string().optional(),
  multiple: z.boolean().default(false).optional(),
  accept: z.string().optional(),
  onClick: z.function().optional(),
})

export type IFormVariable = z.infer<typeof FormVariable>

export type IFormData = {
  [key: string]: string | number | boolean
}

export type IFieldValidateValue = { value: string | number | boolean }

export type IFormValidationData = {
  [key: string]: any
}

export enum ALERT_TYPE {
  INFO,
  SUCCESS,
  WARNING,
  ERROR,
}

export interface IAlert {
  type: ALERT_TYPE
  message: string | React.ReactNode
  durationMs?: number
  closeable?: boolean
}

export interface QueryResponse {
  response: string
}

export interface QueryReferences {
  chunk_id: string
  chunk_url: string
  document_url: string
  document_text: string
  modality: string
}

export type QueryContents = {
  HumanQuestion?: string
  AIResponse?: string
  AIReferences?: QueryReferences[]
}

export type ChatContents = {
  HumanInput?: string
  AIOutput?: string
  FileURL?: string
  FileContentsBase64?: string
  FileType?: string
}

export type Query = {
  archived_at_timestamp: string | null
  archived_by: string
  created_by: string
  created_time: string
  deleted_at_timestamp: string | null
  deleted_by: string
  id: string
  last_modified_by: string
  last_modified_time: string
  llm_type: string | null
  title: string | null
  prompt: string
  user_id: string
  history: QueryContents[]
  query_result?: QueryResponse
  query_references?: QueryReferences[]
  user_query_id?: string
}

export type Chat = {
  archived_at_timestamp: string | null
  archived_by: string
  created_by: string
  created_time: string
  deleted_at_timestamp: string | null
  deleted_by: string
  id: string
  last_modified_by: string
  last_modified_time: string
  prompt: string
  llm_type: string | null
  title: string
  user_id: string
  agent_name: string | null
  history: ChatContents[]
}

export const QUERY_ENGINE_TYPES = {
  "qe_vertex_search": "Vertex Search",
  "qe_llm_service": "GENIE Search",
  "qe_integrated_search": "Integrated Search"
}

export type QueryEngine = {
  id: string
  name: string
  archived_at_timestamp: string | null
  archived_by: string
  created_by: string
  created_time: string
  deleted_at_timestamp: string | null
  deleted_by: string
  last_modified_by: string
  last_modified_time: string
  llm_type: string | null
  parent_engine_id: string
  user_id: string
  query_engine_type: string
  description: string
  embedding_type: string
  vector_store: string | null
  is_public: boolean | null
  index_id: string | null
  index_name: string | null
  endpoint: string | null
  doc_url: string | null
  manifest_url: string | null
  // TODO: The params field is used by the ORM object for storing
  // a map of possible keys and values, which is not reflected in the
  // current QueryEngine interface
  params: {
    is_multimodal: string
    // typing for an object with any fields taken from
    // https://stackoverflow.com/questions/42723922
    [key: string]: any
  } | null
  depth_limit: number | null
  chunk_size: number | null
  agents: string[] | null
  child_engines: string[] | null
  is_multimodal: boolean | null
}

export type QueryEngineBuildParams = {
  depth_limit: string | null
  agents: string | null
  associated_engines: string | null
  manifest_url: string | null
}

export type QueryEngineBuild = {
  user_id: string
  doc_url: string
  query_engine: string
  query_engine_type: string
  llm_type: string
  embedding_type: string
  vector_store: string
  description: string
  params: QueryEngineBuildParams
}

export type QueryEngineBuildJob = {
  id: string
  uuid: string
  name: string
  archived_at_timestamp: string | null
  archived_by: string
  created_by: string
  created_time: string
  deleted_at_timestamp: string | null
  deleted_by: string
  last_modified_by: string
  last_modified_time: string
  type: string
  status: string
  input_data: QueryEngineBuild
  result_data: any
  message: string
  generated_item_id: any
  output_gcs_path: any
  errors: any
  job_logs: any
  metadata: any
}
