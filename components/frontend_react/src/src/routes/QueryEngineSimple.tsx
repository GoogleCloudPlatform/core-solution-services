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
import { fetchAllEngines, createQueryEngine } from "@/utils/api"
import Loading from "@/navigation/Loading"
import { QueryEngine, QueryEngineBuildJob } from "@/utils/types"
import React, { useEffect, useState } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { ALERT_TYPE, IFormVariable } from "@/utils/types"
import { Link, useNavigate } from "react-router-dom"
import { useQueryParams } from "@/utils/routing"
import { userStore, alertStore } from "@/store"

interface IQueryEngineProps {
  token: string
}

const QUERY_ENGINE_SIMPLE_FORM_DATA: IFormVariable[] = [
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
    name: "file_upload",
    display: "Files",
    type: "file(upload)",
    placeholder: "Upload files to bucket",
    description: "",
    default: "",
    required: false,
    group: "queryengine",
    order: 3,
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
]

const QueryEngineSimple: React.FC<IQueryEngineProps> = ({ token }) => {
  const [formError, setFormError] = useState(false)
  const [formSubmitted, setFormSubmitted] = useState(false)
  const isAdmin = true // TODO: userStore((state) => state.isAdmin)
  
  const setAlert = alertStore((state) => state.setAlert)

  const buildQueryEngine = useMutation({
    mutationFn: createQueryEngine(token),
  })

  const onSubmit = async (newQueryEngine: QueryEngine) => {
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
  const onSuccess = () => setFormSubmitted(true)
  const onFailure = (error: unknown) => {
    setFormError(true)
    console.error("Failed to submit QueryEngine", error)
    setAlert({
      message: "Failed to submit QueryEngine",
      type: ALERT_TYPE.ERROR,
    })
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
          <div className="w-full justify-center rounded-lg border-2 border-primary border-opacity-50 p-4 md:flex">
            <QueryEngineForm
              key="simple"
              onSubmit={onSubmit}
              onSuccess={onSuccess}
              onFailure={onFailure}
              queryEngine={null}
              token={token || ""}
              currentVarsData={QUERY_ENGINE_SIMPLE_FORM_DATA}
            />
          </div>

          <input
            type="checkbox"
            id="delete-queryEngine-modal"
            className="modal-toggle"
          />
        </div>
      </div>
    </div>
  )
}

export default QueryEngineSimple
