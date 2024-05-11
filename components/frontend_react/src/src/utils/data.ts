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
