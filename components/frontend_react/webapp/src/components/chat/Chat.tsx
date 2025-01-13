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
import { fetchChat, createChat, resumeChat, updateChat } from "@/utils/api"
import { Chat, ChatContents, IFormVariable } from "@/utils/types"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useConfig } from "@/contexts/configContext"
import Loading from "@/navigation/Loading"

interface GenAIChatProps {
  userToken: string
  initialChatId: string | null
}

const initialOutput = { AIOutput: "Welcome! How can I assist you today?" }
const errMsg = { AIOutput: "I'm sorry, the request could not be completed. A network error was detected." }
const chatError = { AIOutput: "I could not fetch the chat history. A network error was detected." }

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
  const [streamingMessage, setStreamingMessage] = useState("")

  const handleFiles = (_files: FileList | null, _uploadVariable: IFormVariable) => {
    if (_uploadVariable.name == "file_upload" && _files) {
      setUploadFile(_files[0])
      _uploadVariable.value = null
    } else if (_uploadVariable.name == "doc_url" && _files) {
      setFileUrl(_files[0])
      _uploadVariable.value = ""
    } else if (_files?.length === 0) {
      setFileUrl(null)
      setUploadFile(null)
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
    if ((newChatId && newChatId === initialChatId) || (newChatId && !initialChatId)) {
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

  const updateUrlParam = (chatId: string | null) => {
    if (chatId) {
      window.history.replaceState({}, '', `?chat_id=${chatId}`)
    }
  }

  // Helper function to handle streaming response
  const handleStream = async (stream: ReadableStream) => {
    const reader = stream.getReader()
    const decoder = new TextDecoder()
    let accumulatedResponse = ""

    try {
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        accumulatedResponse += chunk
        setStreamingMessage(accumulatedResponse)
      }
      return accumulatedResponse
    } finally {
      reader.releaseLock()
    }
  }

  const onSubmit = async (userInput: string, doc_url: string, tools: string[]) => {
    setActiveJob(true)
    setStreamingMessage("")
    setMessages((prev) => [...prev, { HumanInput: userInput }])

    try {
      if (initialChatId) {
        const response = await resumeChat(userToken)({
          chatId: initialChatId,
          userInput,
          llmType: selectedModel,
          toolNames: tools,
          stream: true
        })
        if (response instanceof ReadableStream) {
          const fullResponse = await handleStream(response)
          // Update messages with both the user input and AI response
          const finalMessages = ((tools.length === 0) ?
            [...messages, { HumanInput: userInput }, { AIOutput: fullResponse }] :
            JSON.parse(fullResponse)['data']['history'])
          setMessages(finalMessages)
          setStreamingMessage("")
          setActiveJob(false)
          // Update the chat with the new history
          await updateChat(userToken)({
            chatId: initialChatId,
            history: finalMessages
          })
          setResumeChatId(initialChatId)
        }
      } else {
        const response = await createChat(userToken)({
          userInput,
          llmType: selectedModel,
          uploadFile,
          fileUrl: doc_url,
          toolNames: tools,
          stream: true
        })

        if (response instanceof ReadableStream) {
          const fullResponse = await handleStream(response)
          // Update messages with the streamed response
          const updatedMessages = ((tools.length === 0) ?
            [...messages, { HumanInput: userInput }, { AIOutput: fullResponse }] :
            JSON.parse(fullResponse)['data']['history'])
          setMessages(updatedMessages)
          setStreamingMessage("")
          setActiveJob(false)
          // Create permanent chat with accumulated history
          if (tools.length === 0) {
            const newChat = await createChat(userToken)({
              userInput: userInput,
              llmType: selectedModel,
              uploadFile,
              fileUrl: doc_url,
              stream: false,
              history: updatedMessages // Pass full message history
            })

            if (newChat && 'id' in newChat) {
              setNewChatId(newChat.id)
            }
          } else {
            // TODO: When tools are present the response is still treated as
            // a streaming response, requireming extra checks to determine
            // how to handle the streaming response. This should be resoved
            // by better understanding how the repsonse is set and
            // ensuring that tool based responses are non-streaming
            const response = JSON.parse(fullResponse)
            setNewChatId(response['data']['id'])
          }
        }
      }
    } catch (error: any) {
      console.error(error)
      setActiveJob(false)
      setMessages((prev) => [...prev, { AIOutput: error.message }])
    } finally {
      setFileUrl(null)
      setUploadFile(null)
      // streaming messages and the active job tracker are cleared here
      // as a final catch in case
      // of an errror but are intended to be cleared previously once
      // the stream has finished sending text
      setStreamingMessage("")
      setActiveJob(false)
    }
  }

  if (initialChatId && isLoading) return <Loading />

  return (
    <div className="bg-primary/20 flex flex-grow gap-4 rounded-lg p-3">
      <div className="bg-base-100 flex w-full rounded-lg chat-p justify-center py-6">
        <ChatWindow
          onSubmit={onSubmit}
          messages={messages}
          activeJob={activeJob}
          handleFiles={handleFiles}
          streamingMessage={streamingMessage}
        />
      </div>
    </div>
  )
}

export default GenAIChat
