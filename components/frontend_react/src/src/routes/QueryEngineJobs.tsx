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

import Loading from "@/navigation/Loading"
import { fetchAllEngineJobs, getEngineJobStatus } from "@/utils/api"
import { classNames } from "@/utils/dom"
import { QueryEngineBuildJob } from "@/utils/types"
import { useQuery } from "@tanstack/react-query"
import dayjs from "dayjs"
import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

interface QueryEngineJobProps {
  token: string
}

const MAX_ENGINE_DISPLAY = 20

const QueryEngineJobs: React.FC<QueryEngineJobProps> = ({ token }) => {
  const [queryEngineJobs, setQueryEngineJobs] = useState<QueryEngineBuildJob[]>([])

  const { data: engineJobList, isLoading, error: engineJobsError } = useQuery(
    ["fetchEngineJobs"], 
    fetchAllEngineJobs(token)
  )

  useEffect(() => {
    setQueryEngineJobs(engineJobList ?? [])
  }, [engineJobList])

  // Poll for job status
  const [pollIntervalId, setPollIntervalId] = useState(null)

  useEffect(() => {  
    const pollJobStatus = async () => {
      jobRunning = false
      queryEngineJobs.map(job, i) => (
        if (job.status === "pending" || job.status === "running") {
          try {
            const jobUpdate = await getEngineJobStatus(job.name, token)
            queryEngineJobs[i].status = jobUpdate?.status
          } catch (error) {
            console.log("Error polling")
          }
          jobRunning = true
        }
      )
      if (!jobRunning) {
        clearInterval(pollIntervalId)
      }
    }

    // Set up the interval to poll every second
    const intervalId = setInterval(pollJobStatus, 1000)
    setPollIntervalId(intervalId)

    // Cleanup: Clear the interval when the component unmounts
    return () => clearInterval(intervalId);

  }, [queryEngineJobs, token])

  if (isLoading) return <Loading />

  return (
    <div className="overflow-x-auto custom-scrollbar">
      <table className="table-lg table-zebra table w-full">
        {/* head */}
        <thead>
          <tr className="text-left">
            <th>Engine Name</th>
            <th>Job ID</th>
            <th>Job Status</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody className="opacity-80">
          {queryEngineJobs
            .sort((a, b) => (b.created_time > a.created_time ? 1 : -1))
            .slice(0, MAX_ENGINE_DISPLAY)
            .map((job, i) => (
              <tr
                key={job.name}
                className={classNames(
                  "text-sm lg:text-base",
                  i % 2 === 0 ? "bg-base-200" : "bg-base-100",
                )}
              >
                <td className="text-sm lg:text-base">
                  <Link
                    to={`/aiquery`}
                    className="text-primary text-sm transition hover:underline lg:text-base"
                  >
                    {job.input_data.query_engine}
                  </Link>
                </td>
                <td className="text-xs md:text-sm lg:min-w-56 lg:text-base">
                  {job.name}
                </td>
                <td className="text-xs md:text-sm lg:min-w-56 lg:text-base">
                  {job.status}
                </td>
                <td className="text-xs md:text-sm lg:min-w-56 lg:text-base">
                  {dayjs(job.created_time).format("MMM D, YYYY • h:mm A")}
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  )
}

export default QueryEngineJobs
