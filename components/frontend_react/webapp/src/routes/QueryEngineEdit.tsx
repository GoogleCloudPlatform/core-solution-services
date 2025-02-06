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

import QueryEngineForm from "@/components/forms/QueryEngineForm"
import Header from "@/components/typography/Header"
import { fetchAllEngines, createQueryEngine, updateQueryEngine, deleteQueryEngine } from "@/utils/api"
import Loading from "@/navigation/Loading"
import { QUERY_ENGINE_FORM_DATA } from "@/utils/data"
import { QueryEngine, QueryEngineBuildJob } from "@/utils/types"
import { TrashIcon } from "@heroicons/react/24/outline"
import React, { useEffect, useState } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { ALERT_TYPE } from "@/utils/types"
import { Link, useNavigate } from "react-router-dom"
import { useQueryParams } from "@/utils/routing"
import { userStore, alertStore } from "@/store"
import { fetchEmbeddingTypes } from "@/utils/api"

interface IQueryEngineProps {
  token: string
}

const QueryEngineEdit: React.FC<IQueryEngineProps> = ({ token }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [activeJob, setActiveJob] = useState(false)
  const [formError, setFormError] = useState(false)
  const [formSubmitted, setFormSubmitted] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const isAdmin = true // TODO: userStore((state) => state.isAdmin)

  const params = useQueryParams()
  const id = params.get("id")
  const navigate = useNavigate()

  const setAlert = alertStore((state) => state.setAlert)

  const [queryEngines, setQueryEngines] = useState<QueryEngine[]>([])
  const [queryEngine, setQueryEngine] = useState<QueryEngine | null>(null)
  const [createEngineIsMultimodal, setCreateEngineIsMultimodal] = useState(false)
  const [createEngineEmbeddingOptions, setCreateEngineEmbeddingOptions] = useState<{ option: string; value: string; }[]>([])
  const [queryEngineFiles, setQueryEngineFiles] = useState<FileList | null>(null)

  const openDeleteModal = () => {
    setIsModalOpen(true)
    const modalToggle = document.getElementById('delete-queryEngine-modal')
    modalToggle.checked = true
  }
  const closeDeleteModal = () => {
    setIsModalOpen(false)
    const modalToggle = document.getElementById('delete-queryEngine-modal')
    modalToggle.checked = false
  }

  const { isLoading, data: engineList } = useQuery(
    ["QueryEngines"],
    fetchAllEngines(token),
  )

  useEffect(() => {
    setQueryEngines(engineList ?? [])
  }, [engineList])

  useEffect(() => {
    if (!queryEngines || !id) return
    const queryEngineToUpdate = queryEngines.find((d) => d.id === id) ?? null
    setQueryEngine(queryEngineToUpdate)
  }, [queryEngines])

  const buildQueryEngine = useMutation({
    mutationFn: createQueryEngine(token),
  })

  const updateQEngine = useMutation({
    mutationFn: updateQueryEngine(token),
  })

  const deleteQEngine = useMutation({
    mutationFn: deleteQueryEngine(token),
  })

  const onSubmit = async (newQueryEngine: QueryEngine) => {
    // Update existing queryEngine
    if (queryEngine) {
      updateQEngine.mutate(
        queryEngine,
        {
          onSuccess: (resp?: QueryEngineBuildJob) => {
            // TODO
          },
          onError: () => {
            setActiveJob(false)
            // TODO
          }
        }
      )
    }
    // Else, create a new queryEngine
    else {
      buildQueryEngine.mutate(
        newQueryEngine,
        {
          onSuccess: (resp?: QueryEngineBuildJob) => {
            setAlert({
              message: "Submitted QueryEngine Build Job: " + resp.name,
              type: ALERT_TYPE.SUCCESS,
            })
          },
          onError: () => {
            setActiveJob(false)
            // TODO
          }
        }
      )
    }
  }
  const onSuccess = () => setFormSubmitted(true)
  const onFailure = (error: unknown) => {
    setFormError(true)
    console.error("Failed to submit QueryEngine", error)
    setAlert({
      message: "Failed to submit QueryEngine",
      type: ALERT_TYPE.ERROR,
    })
  }

  const deleteQueryEngineDetails = async () => {
    if (!queryEngine) throw new Error("No id of queryEngine to delete")

    setDeleting(true)
    setActiveJob(true)
    deleteQEngine.mutate(
      queryEngine,
      {
        onSuccess: (resp?: boolean) => {
          if (resp) {
            setAlert({
              message: "Deleted successfully!",
              type: ALERT_TYPE.SUCCESS,
              durationMs: 4000,
            })
          }
          setDeleting(false)
          setActiveJob(false)
          closeDeleteModal()
          navigate("/queryengines")
        },
        onError: () => {
          setAlert({
            message: "Error occurred deleting",
            type: ALERT_TYPE.ERROR,
            durationMs: 4000,
          })
          setDeleting(false)
          setActiveJob(false)
          closeDeleteModal()
          navigate("/queryengines/admin")
        }
      }
    )
  }

  useEffect(() => {
    if (formSubmitted) {
      setAlert({
        message: "Updated successfully!",
        type: ALERT_TYPE.SUCCESS,
        durationMs: 4000,
      })
      window.scrollTo(0, 0)
      setFormSubmitted(false)
    }

    if (formError) {
      setAlert({
        message:
          "Something went wrong. Please sign out and back in, and try again. If the problem persists, contact us at gps-rit@google.com",
        type: ALERT_TYPE.ERROR,
      })
      setFormError(false)
    }
  }, [formSubmitted, formError])

  if (!isAdmin) {
    return <Loading />
  }

  const updatedQueryEngineFormData = QUERY_ENGINE_FORM_DATA.map(
    (entry) => {
      switch (entry.name) {
        case "is_multimodal":
          return { ...entry, onClick: () => { setCreateEngineIsMultimodal(!createEngineIsMultimodal) } }
        case "embedding_type":
          return { ...entry, options: createEngineEmbeddingOptions }
        default:
          return entry
      }
    })

  useEffect(() => {
    const updateEngineEmbeddings = async () => {
      const llmTypes = await (await fetchEmbeddingTypes(token, createEngineIsMultimodal))()
      if (llmTypes === null || llmTypes === undefined) console.error("Failed to retrieve embedding types")
      else setCreateEngineEmbeddingOptions(llmTypes.map((embedding) => { return { option: embedding, value: embedding } }))
    }
    updateEngineEmbeddings()
  },
    [createEngineIsMultimodal])

  return (
    <div className="overflow-x-auto custom-scrollbar">
      <div className="min-h-screen">
        <div>
          <div className="relative">
            {queryEngine && (
              <>
                <Link href={`/queryengines/detail?id=${queryEngine.id}`}>
                  <button className="btn btn-outline btn-sm cursor-pointer absolute right-20 top-0 z-10">
                    View Details
                  </button>
                </Link>
                <button className="absolute right-0 top-0 z-10" onClick={openDeleteModal}>
                  <TrashIcon className="text-dim hover:text-normal w-8 cursor-pointer text-error transition" />
                </button>
              </>
            )}
            <div className="flex flex-col">
              <div className="mb-4 text-xl font-bold">
                <Header>{`${queryEngine?.id ? "Update" : "Add"} QueryEngine`}</Header>
                {queryEngine?.name && (
                  <span className="text-sm">{`(${queryEngine.name})`}</span>
                )}
              </div>
            </div>
          </div>

          <div className="w-full justify-center rounded-lg border-2 border-primary border-opacity-50 p-4 md:flex">
            <QueryEngineForm
              key={queryEngine?.id}
              onSubmit={onSubmit}
              onSuccess={onSuccess}
              onFailure={onFailure}
              queryEngine={queryEngine}
              currentVarsData={updatedQueryEngineFormData}
            />
          </div>

          <input
            type="checkbox"
            id="delete-queryEngine-modal"
            className="modal-toggle"
          />
          <div className="modal">
            <div className="modal-box">
              <h3 className="text-lg font-bold">
                {/* @ts-ignore */}
                Delete "{queryEngine?.name || "QueryEngine"}"?
              </h3>
              <p className="py-4">This action cannot be undone</p>
              <div className="modal-action">
                {activeJob && (
                  <i className="i-svg-spinners-180-ring text-info group-hover:text-base-content/100 transition h-6 w-6 shrink-0"></i>
                )}
                <button className="btn btn-outline" onClick={closeDeleteModal}>
                  Cancel
                </button>
                <button
                  className="btn btn-error"
                  disabled={deleting}
                  onClick={deleteQueryEngineDetails}
                >
                  {deleting ? "Deleting" : "Delete"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default QueryEngineEdit
