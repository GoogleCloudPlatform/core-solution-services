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

import { useState } from "react"
import QueryEngineForm from "@/components/forms/QueryEngineForm"

interface QueryInputProps {
  onSubmit: (message: string) => void
  onUploadSubmit: Function
  onUploadSuccess: Function
  onUploadFailure: Function
  handleFiles: Function
  token: string
  activeJob: boolean
}

const QUERY_UPLOAD_FORM_DATA: IFormVariable[] = [
  {
    name: "doc_url",
    display: "Document URL to query",
    type: "string",
    placeholder: "http(s)://, gs://, bq://<table>, shpt://",
    description: "",
    default: "",
    required: true,
    group: "queryengine",
    order: 1,
  },
  {
    name: "file_upload",
    display: "Files",
    type: "file(upload)",
    placeholder: "Upload files to query",
    description: "",
    default: "",
    required: false,
    group: "queryengine",
    order: 2,
  },
]

const QueryInput: React.FC<QueryInputProps> = ({ onSubmit, onUploadSubmit, onUploadSuccess, onUploadFailure, handleFiles, token, activeJob }) => {
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  
  const handleUploadClick = () => {
    setIsUploadOpen((prev) => !prev)
  }

  return (
    <div>    
      <form
        className="flex items-center gap-4"
        onSubmit={(e) => {
          e.preventDefault()
          const input = document.getElementById("chat-input") as HTMLInputElement
          onSubmit(input.value)
          input.value = ""
        }}
      >
        <input
          className="border-base-content/50 w-full outline-none focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary rounded-xl border p-3 placeholder:text-sm transition"
          id="chat-input"
          type="text"
          placeholder="Enter a prompt here"
          autoComplete="off"
        />
        <div
          onClick={handleUploadClick}
          className={"flex rounded-lg items-center text-start text-sm p-2.5 group bg-base-100 hover:bg-base-200 transition cursor-pointer"}
        >
          <div className="i-heroicons-plus-circle h-8 w-8 shrink-0 hover:text-info transition" />
        </div>
        <button
          type="submit"
          disabled={activeJob}
          className={`group rounded-full p-2 transition ${
            activeJob ? 'bg-base-100 text-base-content/50' : 'hover:bg-base-200 text-base-content/75'
          }`}
        >
          <div className="i-material-symbols-send-outline-rounded h-8 w-8 shrink-0" />
        </button>
      </form>
      {isUploadOpen && <div className="w-full justify-center rounded-lg border-2 border-primary border-opacity-50 p-4 md:flex">
         <QueryEngineForm
          key="upload"
          onSubmit={onUploadSubmit}
          onSuccess={onUploadSuccess}
          onFailure={onUploadFailure}
          handleFiles={handleFiles}
          queryEngine={null}
          token={token || ""}
          currentVarsData={QUERY_UPLOAD_FORM_DATA}
          />
      </div>}
    </div>
  )
}

export default QueryInput
