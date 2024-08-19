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
import QueryWindow from "@/components/query/QueryWindow"
import { fetchQuery, createQuery, resumeQuery, uploadQueryFile } from "@/utils/api"
import { Query, QueryContents } from "@/utils/types"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import { useConfig } from "@/contexts/configContext"
import Loading from "@/navigation/Loading"

interface GenAIQueryProps {
  userToken: string
  initialQueryId: string | null
}

const initialOutput = {AIOutput: "Welcome! How can I assist you today?"}
const errMsg = {AIOutput: "I'm sorry, the request could not be completed. A network error was detected."}
const queryError = {AIOutput: "I could not fetch the query history. A network error was detected."}

const GenAIQuery: React.FC<GenAIQueryProps> = ({
  userToken,
  initialQueryId,
}) => {

  const [messages, setMessages] = useState<QueryContents[]>([initialOutput])
  const [activeJob, setActiveJob] = useState(false)
  const [newQueryId, setNewQueryId] = useState<string | null>(null)
  const [resumeQueryId, setResumeQueryId] = useState<string | null>(null)
  const initialQueryRef = useRef(initialQueryId)
  const [uploadFiles, setUploadFiles] = useState<FileList | null>(null)

  const { selectedModel, selectedEngine } = useConfig()

  const handleFiles = (_files: FileList, _uploadVariable: string) => {
    console.log("handleFiles")
    setUploadFiles(_files)
  }

  const {
    isLoading,
    data: query,
    refetch,
    isError,
  } = useQuery(["Query", initialQueryId], fetchQuery(userToken, initialQueryId ?? ""),
    { enabled: !!initialQueryId }
  )

  useEffect(() => {
    // Clear loading indicator when the query ID changes
    if (initialQueryId && initialQueryId !== initialQueryRef.current) {
      setActiveJob(false)
    }
    // Clears loading indicator when a new query is pending but the ID has changed
    if (activeJob && !initialQueryId) {
      setActiveJob(false)
    }
  }, [initialQueryId])

  // Handle onSuccess from creating a query
  useEffect(() => {
    if (!newQueryId) return
    if ((newQueryId && newQueryId == initialQueryId) || (newQueryId && !initialQueryId)) {
      updateUrlParam(newQueryId)
      initialQueryRef.current = newQueryId
      setActiveJob(false)
      setNewQueryId(null)
    }
  }, [newQueryId])

  // Handle onSuccess from resuming a query
  useEffect(() => {
    if (resumeQueryId && resumeQueryId == initialQueryId) {
      initialQueryRef.current = resumeQueryId
      setActiveJob(false)
      setResumeQueryId(null)
    } else if (resumeQueryId && resumeQueryId != initialQueryId) {
      initialQueryRef.current = initialQueryId
      setActiveJob(false)
      setResumeQueryId(null)
    } else {
      return
    }
  }, [resumeQueryId])

  // Once the query history is fetched, clear or set msgs and refs
  useEffect(() => {
    query?.history ? setMessages(query.history) : setMessages([initialOutput])
    !initialQueryId && setMessages([initialOutput])
  }, [query])

  // Handle error from fetching query history
  useEffect(() => {
    if (isError) {
      setMessages((prev) => [...prev, queryError])
    }
  }, [isError])

  const addQuery = useMutation({
    mutationFn: createQuery(userToken),
  })

  const continueQuery = useMutation({
    mutationFn: resumeQuery(userToken),
  })

  const uploadQuery = useMutation({
    mutationFn: uploadQueryFile(userToken),
  })

  const navigate = useNavigate()

  const updateUrlParam = (queryId: string | null) => {
    navigate(`?query_id=${queryId}`, { replace: true })
  }

  const onUploadSubmit = (userInput: string) => {
    console.log("onUploadSubmit")
    uploadQuery.mutate(
      {
        queryId: initialQueryId,
        userInput,
        llmType: selectedModel,
        uploadFile: uploadFiles[0]
      },
      {
        onSuccess: (resp?: QueryEngine) => {
          const currQueryId = resp?.id.toString() ?? null

          if (currQueryId) {
            setResumeQueryId(currQueryId)
            refetch()
          }
        },
        onError: () => {
          setActiveJob(false)
          setMessages((prev) => [...prev, errMsg])
        }
      }
    )
  }

  const onUploadSuccess = (userInput: string) => {
    console.log("onUploadSuccess")
  }

  const onUploadFailure = (userInput: string) => {
    console.log("onUploadFailure")
  }


  const onSubmit = (userInput: string) => {
    setActiveJob(true)

    // Display user prompt in chat immediately
    setMessages((prev) => [...prev, { HumanQuestion: userInput }])

    // Resume query if an ID param is set, otherwise create a query
    if (initialQueryId) {
      continueQuery.mutate(
        {
          queryId: initialQueryId,
          userInput,
          llmType: selectedModel,
        },
        {
          onSuccess: (resp?: Query) => {
            const currQueryId = resp?.toString() ?? null

            if (currQueryId) {
              setResumeQueryId(currQueryId)
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
      addQuery.mutate(
        {
          engine: selectedEngine,
          userInput,
          llmType: selectedModel,
        },
        {
          onSuccess: (resp?: Query) => {
            const updatedQueryId = resp?.toString() ?? null

            if (updatedQueryId) {
              setNewQueryId(updatedQueryId)
            }
          },
          onError: () => {
            setActiveJob(false)
            setMessages((prev) => [...prev, errMsg])
          }
        }
      )
    }
  }

  if (initialQueryId && isLoading) return <Loading />

  return (
    <div className="bg-primary/20 flex flex-grow gap-4 rounded-lg p-3">
      <div className="bg-base-100 flex w-full rounded-lg chat-p justify-center py-6">
        <QueryWindow onSubmit={onSubmit} messages={messages} activeJob={activeJob} token={userToken}
                     onUploadSubmit={onUploadSubmit} onUploadSuccess={onUploadSuccess}
                     onUploadFailure={onUploadFailure} handleFiles={handleFiles}
        />
      </div>
    </div>
  )
}

export default GenAIQuery
