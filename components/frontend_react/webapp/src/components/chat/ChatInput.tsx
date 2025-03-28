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
import ChatUploadForm from "@/components/forms/ChatUploadForm"

interface ChatInputProps {
  onSubmit: (message: string,
    doc_url: string | null,
    tool_names: string[]) => void
  activeJob: boolean,
  handleFiles: Function
}

const CHAT_UPLOAD_FORM_DATA: IFormVariable[] = [
  {
    name: "doc_url",
    display: "Document URL",
    type: "string",
    placeholder: "http(s)://, gs://, shpt://",
    description: "",
    default: "",
    required: false,
    group: "chatupload",
    order: 1,
  },
  {
    name: "file_upload",
    display: "File",
    type: "file(upload)",
    placeholder: "Upload file",
    fileLabel: "Select local file",
    multiple: false,
    description: "",
    default: "",
    required: false,
    group: "chatupload",
    order: 2,
  },
]

const ChatInput: React.FC<ChatInputProps> = ({ onSubmit, activeJob, handleFiles }) => {
  const [isUploadOpen, setIsUploadOpen] = useState(false)
  const [toolNames, setToolNames] = useState<string[]>([])
  // changed to reset the upload files when the chat is submitted
  const [chatUploadResetkey, setChatUploadResetkey] = useState(1)

  const handleUploadClick = () => {
    setIsUploadOpen((prev) => !prev)
  }

  const handleToolsClick = () => {
    setToolNames(
      (prev) => prev.length > 0 ? [] : ["vertex_code_interpreter_tool"])
  }

  return (
    <div>
      <form
        className="flex items-center gap-4"
        onSubmit={(e) => {
          e.preventDefault()
          const input = document.getElementById("chat-input") as HTMLInputElement
          const doc_url = document.getElementById("doc_url") as HTMLInputElement | null
          if (input?.value !== null && input?.value !== "") {
            onSubmit(input.value, doc_url?.value || "", toolNames)
            handleFiles(null, "")
            setChatUploadResetkey(chatUploadResetkey * -1)
          }
          input.value = ""
          if (doc_url) {
            doc_url.value = ""
          }
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
        <div
          onClick={handleToolsClick}
          title="Code Interpreter - Generates code and graphs to answer questions. Generation may take a few minutes."
          className={"flex rounded-lg items-center text-start text-sm p-2.5 group bg-base-100 hover:bg-base-200 transition cursor-pointer"}
          style={{ "borderRadius": "10px", border: "2px solid", opacity: toolNames.length > 0 ? 1 : .5 }}
        >
          <p>Generate Graph</p>
        </div>
        <button
          type="submit"
          disabled={activeJob}
          className={`group rounded-full p-2 transition ${activeJob ? 'bg-base-100 text-base-content/50' : 'hover:bg-base-200 text-base-content/75'
            }`}
        >
          <div className="i-material-symbols-send-outline-rounded h-8 w-8 shrink-0" />
        </button>
      </form >
      {isUploadOpen &&
        <div key={chatUploadResetkey} className="w-full justify-center rounded-lg border-2 border-primary border-opacity-50 p-4 md:flex">
          <ChatUploadForm
            key="upload"
            handleFiles={handleFiles}
            currentVarsData={CHAT_UPLOAD_FORM_DATA}
          />
        </div>}
    </div >
  )
}

export default ChatInput
