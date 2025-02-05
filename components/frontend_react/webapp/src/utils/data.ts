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

import { Chat, Query, IFormVariable } from "@/utils/types"

export const TEST_FORM_DATA: IFormVariable[] = [
  {
    name: "name",
    display: "Name",
    type: "string",
    description: "",
    default: "",
    required: true,
    group: 1,
  },
  {
    name: "description",
    display: "Description",
    type: "string",
    description: "",
    default: "",
    required: true,
    group: 1,
  },
  {
    name: "option",
    display: "Option",
    type: "select",
    description: "",
    options: ["option1", "option2"],
    default: "option1",
    required: false,
    group: 1,
  },
  {
    name: "link",
    display: "Primary Link",
    type: "string",
    description: "",
    default: "",
    required: false,
    group: 2,
  },
  {
    name: "otherLinks",
    display: "Other Links",
    type: "list(string)",
    description: "",
    default: [],
    required: false,
    group: 2,
  },
  {
    name: "supportingFiles",
    display: "Upload Files",
    tooltip: "Upload manuals/documentation",
    type: "file",
    description: "",
    default: [],
    required: false,
    fileLabel: "Supporting Files",
    multiple: true,
    accept: "image/*,.pdf,.docx,.doc,.ppt,.xls",
    group: 2,
  },
  {
    name: "uploadFiles",
    display: "Select Files",
    tooltip: "Select files to upload",
    type: "file(upload)",
    description: "",
    default: null,
    required: false,
    fileLabel: "Relevant Files",
    group: 2
  }
]

export const QUERY_ENGINE_FORM_DATA: IFormVariable[] = [
  {
    name: "name",
    display: "Name",
    type: "string",
    placeholder: "Name of the Query Engine. Can include spaces.",
    default: "",
    required: true,
    group: "queryengine",
    order: 1,
  },
  {
    name: "query_engine_type",
    display: "Query Engine Type",
    tooltip: "Type of Query Engine. GENIE is the native type.",
    type: "select",
    description: "",
    options: [{ option: "Vertex Search", value: "qe_vertex_search" },
    { option: "GENIE Search", value: "qe_llm_service" },
    { option: "Integrated Search", value: "qe_integrated_search" }],
    default: "GENIE",
    required: true,
    group: "queryengine",
    order: 1,
  },
  {
    name: "is_multimodal",
    display: "Multimodal Engine",
    tooltip: "Type of Query Engine. GENIE is the native type.",
    type: "bool",
    description: "",
    default: false,
    required: true,
    group: "queryengine",
    order: 1,
  },
  {
    name: "doc_url",
    display: "Data URL",
    type: "string",
    placeholder: "http(s)://, gs://, bq://<table>, shpt://",
    description: "",
    default: "",
    required: true,
    group: "queryengine",
    order: 2,
  },
  {
    name: "uploadFiles",
    display: "Select Files",
    tooltip: "Select files to upload",
    type: "file(upload)",
    description: "",
    default: null,
    multiple: true,
    required: false,
    fileLabel: "Relevant Files",
    group: "queryengine",
    order: 2
  },
  {
    name: "manifest_url",
    display: "Manifest URL",
    type: "string",
    placeholder: "Manifest URL for document metadata: gs://<file.json>",
    description: "",
    default: "",
    required: false,
    group: "queryengine",
    order: 3,
  },
  {
    name: "vector_store",
    display: "Vector Store",
    type: "select",
    description: "",
    options: [{ option: "PGVector", value: "langchain_pgvector" },
    { option: "Vertex Matching Engine", value: "matching_engine" }],
    default: "PGVector",
    required: true,
    group: "queryengine",
    order: 4,
  },
  {
    name: "embedding_type",
    display: "Embedding Type",
    type: "select",
    description: "",
    options: [],
    default: "Vertex",
    required: true,
    group: "queryengine",
    order: 4,
  },
  {
    name: "depth_limit",
    display: "Depth Limit",
    type: "select",
    description: "The depth to crawl for web data sources.",
    options: [0, 1, 2, 3, 4],
    default: 0,
    required: false,
    group: "queryengine",
    order: 4,
  },
  {
    name: "chunk_size",
    display: "Chunk Size",
    type: "select",
    description: "Chunking size for RAG.  Smaller is better for accuracy but makes builds take significantly longer.",
    options: [50, 100, 200, 300, 400, 500],
    default: "500",
    required: false,
    group: "queryengine",
    order: 4,
  },
  {
    name: "description",
    display: "Description",
    type: "string",
    description: "",
    default: "",
    required: false,
    group: "queryengine",
    order: 5,
  },
  {
    name: "agents",
    display: "Agents",
    type: "string",
    description: "",
    placeholder: "Comma separated list of agents that have access to this query engine",
    default: "",
    required: false,
    group: "queryengine",
    order: 6,
  },
  {
    name: "child_engines",
    display: "Child Engines",
    type: "string",
    description: "",
    placeholder: "Comma separated list of child engines (only for integrated search types)",
    default: "",
    required: false,
    group: "queryengine",
    order: 7,
  },
]

export const tableData = [
  {
    productid: "IPhone",
    email: "Debdeep",
    date: "10-12-2021",
    status: "Pending",
  },
  {
    productid: "IPhone",
    email: "Debdeep",
    date: "10-12-2021",
    status: "Approved",
  },
  {
    productid: "IPhone",
    email: "Debdeep",
    date: "10-12-2021",
    status: "Rejected",
  },
  {
    productid: "IPhone",
    email: "Debdeep",
    date: "10-12-2021",
    status: "Approved",
  },
  {
    productid: "IPhone",
    email: "Debdeep",
    date: "10-12-2021",
    status: "Pending",
  },
]

export const tableHeaders = ["ProductID", "Email", "Date", "Status"]

export const fallBackConversations: Chat[] = []

export const fallBackQueries: Query[] = []
