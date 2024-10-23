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

interface IQueryEngineProps {
  token: string
}

const QueryEngineEdit: React.FC<IQueryEngineProps> = ({ token }) => {
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
        },
        onError: () => {
          setAlert({
            message: "Error occurred deleting",
            type: ALERT_TYPE.ERROR,
            durationMs: 4000,
          })            
        }
      }
    )          
    setDeleting(false)
    setActiveJob(false)
    navigate("/queryengines/admin")
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
                <label
                  htmlFor="delete-queryEngine-modal"
                  className="absolute right-0 top-0 z-10"
                >
                  <TrashIcon className="text-dim hover:text-normal w-8 cursor-pointer text-error transition" />
                </label>
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
              handleFiles={null}
              queryEngine={queryEngine}
              currentVarsData={QUERY_ENGINE_FORM_DATA}
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
                <label htmlFor="delete-queryEngine-modal" className="btn btn-outline">
                  Cancel
                </label>
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
