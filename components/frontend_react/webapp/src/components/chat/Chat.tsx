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

import React, { useState, useEffect, useRef } from "react"
import ChatWindow from "@/components/chat/ChatWindow"
import { fetchChat, createChat, resumeChat } from "@/utils/api"
import { Chat, ChatContents, IFormVariable } from "@/utils/types"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { useConfig } from "@/contexts/configContext"
import Loading from "@/navigation/Loading"

interface GenAIChatProps {
  userToken: string
  initialChatId: string | null
}

const initialOutput = {AIOutput: "Welcome! How can I assist you today?"}
const errMsg = {AIOutput: "I'm sorry, the request could not be completed. A network error was detected."}
const chatError = {AIOutput: "I could not fetch the chat history. A network error was detected."}

const GenAIChat: React.FC<GenAIChatProps> = ({
  userToken,
  initialChatId,
}) => {

  const [messages, setMessages] = useState<ChatContents[]>([initialOutput])
  const [activeJob, setActiveJob] = useState(false)
  const [newChatId, setNewChatId] = useState<string | null>(null)
  const [resumeChatId, setResumeChatId] = useState<string | null>(null)
  const initialChatRef = useRef(initialChatId)
  const { selectedModel, selectedEngine } = useConfig()
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [fileUrl, setFileUrl] = useState<string | null>(null)

  const handleFiles = (_files: FileList, _uploadVariable: IFormVariable) => {
    console.log("handleFiles")
    if (_uploadVariable.name == "file_upload") {
      setUploadFile(_files[0])
      _uploadVariable.value = null
      console.log("_files", _files)
    } else if (_uploadVariable.name == "doc_url") {
      setFileUrl(_files[0])
      _uploadVariable.value = ""
      console.log("setFileUrl", _files[0])
    }  
  }

  const {
    isLoading,
    data: chat,
    refetch,
    isError,
  } = useQuery(["Chat", initialChatId], fetchChat(userToken, initialChatId ?? ""),
    { enabled: !!initialChatId }
  )

  useEffect(() => {
    // Clear loading indicator when the chat ID changes
    if (initialChatId && initialChatId !== initialChatRef.current) {
      setActiveJob(false)
    }
    // Clears loading indicator when a new chat is pending but the ID has changed
    if (activeJob && !initialChatId) {
      setActiveJob(false)
    }
  }, [initialChatId])

  // Handle onSuccess from creating a chat
  useEffect(() => {
    if (!newChatId) return
    if ((newChatId && newChatId == initialChatId) || (newChatId && !initialChatId)) {
      updateUrlParam(newChatId)
      initialChatRef.current = newChatId
      setActiveJob(false)
      setNewChatId(null)
    }
  }, [newChatId])

  // Handle onSuccess from resuming a chat
  useEffect(() => {
    if (resumeChatId && resumeChatId == initialChatId) {
      initialChatRef.current = resumeChatId
      setActiveJob(false)
      setResumeChatId(null)
    } else if (resumeChatId && resumeChatId != initialChatId) {
      initialChatRef.current = initialChatId
      setActiveJob(false)
      setResumeChatId(null)
    } else {
      return
    }
  }, [resumeChatId])

  // Once the chat history is fetched, clear or set msgs and refs
  useEffect(() => {
    chat?.history ? setMessages(chat.history) : setMessages([initialOutput])
    !initialChatId && setMessages([initialOutput])
  }, [chat])

  // Handle error from fetching chat history
  useEffect(() => {
    if (isError) {
      setMessages((prev) => [...prev, chatError])
    }
  }, [isError])

  const addChat = useMutation({
    mutationFn: createChat(userToken),
  })

  const continueChat = useMutation({
    mutationFn: resumeChat(userToken),
  })

  const navigate = useNavigate()

  const updateUrlParam = (chatId: string | null) => {
    navigate(`?chat_id=${chatId}`, { replace: true })
  }

  const onSubmit = (userInput: string, doc_url: string) => {
    console.log("doc_url", doc_url)
    setFileUrl(doc_url)
    setActiveJob(true)

    // Display user prompt in chat immediately
    setMessages((prev) => [...prev, { HumanInput: userInput }])

    // Resume chat if an ID param is set, otherwise create a chat
    if (initialChatId) {
      continueChat.mutate(
        {
          chatId: initialChatId,
          userInput,
          llmType: selectedModel,
        },
        {
          onSuccess: (resp?: Chat) => {
            const currChatId = resp?.id ?? null

            if (currChatId) {
              setResumeChatId(currChatId)
              refetch()
            }
          },
          onError: () => {
            setActiveJob(false)
            setMessages((prev) => [...prev, errMsg])
          }
        }
      )
    } else {
      addChat.mutate(
        {
          userInput,
          llmType: selectedModel,
          uploadFile: uploadFile,
          fileUrl: doc_url
        },
        {
          onSuccess: (resp?: Chat) => {
            const updatedChatId = resp?.id ?? null

            if (updatedChatId) {
              setNewChatId(updatedChatId)
            }
            setFileUrl(null)
            setUploadFile(null)
          },
          onError: () => {
            setActiveJob(false)
            setMessages((prev) => [...prev, errMsg])
          }
        }
      )
    }
  }

  if (initialChatId && isLoading) return <Loading />

  return (
    <div className="bg-primary/20 flex flex-grow gap-4 rounded-lg p-3">
      <div className="bg-base-100 flex w-full rounded-lg chat-p justify-center py-6">
        <ChatWindow onSubmit={onSubmit} messages={messages} activeJob={activeJob} handleFiles={handleFiles} />
      </div>
    </div>
  )
}

export default GenAIChat
