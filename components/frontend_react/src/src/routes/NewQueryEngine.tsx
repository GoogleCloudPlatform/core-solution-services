import QueryEngineForm from "@/components/forms/QueryEngineForm"
import Header from "@/components/typography/Header"
import { fetchAllEngines, createQueryEngine } from "@/utils/api"
import Loading from "@/navigation/Loading"
import { QUERY_ENGINE_FORM_DATA } from "@/utils/data"
import { QueryEngine, QueryEngineBuildJob } from "@/utils/types"
import { TrashIcon } from "@heroicons/react/24/outline"
import axios from "axios"
import { useRouter } from "next/router"
import nookies from "nookies"
import React, { useEffect, useState } from "react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { ALERT_TYPE } from "@/utils/types"
import Link from "next/link"

// TODO: import { userStore } from "@/store"
// TODO: import { alertStore } from "@/store"

interface INewQueryEngineProps {
  initialQueryEngineId: string | null
}

const NewQueryEngine: React.FC<INewQueryEngineProps> = () => {
  const router = useRouter()
  const [formError, setFormError] = useState(false)
  const [formSubmitted, setFormSubmitted] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const isAdmin = true   // TODO: userStore((state) => state.isAdmin)
  const { id } = router.query
  const setAlert = alertStore((state) => state.setAlert)

  const [queryEngines, setQueryEngines] = useState<QueryEngine[]>([])
  const [queryEngine, setQueryEngine] = useState<QueryEngine | null>(null)

  const { isLoading, data: queryEngines } = useQuery(
    ["QueryEngines"],
    fetchAllEngines(token),
  )

  useEffect(() => {
    if (!queryEngines || !id) return
    const queryEngineToUpdate = queryEngines.find((d) => d.id === id) ?? null
    setQueryEngine(queryEngineToUpdate)
  }, [queryEngines])

  const token = nookies.get().token
  const options = { headers: { Authorization: `Bearer ${token}` } }

  const buildQueryEngine = useMutation({
    mutationFn: createQueryEngine(token),
  })

  const onSubmit = async (newQueryEngine: QueryEngine) => {
    // Update existing queryEngine
    if (queryEngine) {
      return await axios
        .put(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/query/engine/${queryEngine.id}/`,
          newQueryEngine,
          options,
        )
        .then(async (res) => {
          // Update queryEngines context data
          const updated = [
            ...queryEngines!.filter((d) => d.id !== res.data.queryEngine.id),
            res.data.queryEngine,
          ]
          setFormError(false)
          setQueryEngines(updated)
        })
    }
    // Else, create a new queryEngine
    buildQueryEngine.mutate(
      {
        queryEngine: queryEngine
      },
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
    await axios.delete(
      `${process.env.NEXT_PUBLIC_API_BASE_URL}/query/engine/${queryEngine.id}/`,
      options,
    )
    router.push("/", undefined, { shallow: true })
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
                <Link href={`/query/engine/${queryEngine.id}/`}>
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
              queryEngine={queryEngine}
              token={token || ""}
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

export default NewQueryEngine
