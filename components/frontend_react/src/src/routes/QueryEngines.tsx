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
import { fetchAllEngines } from "@/utils/api"
import { classNames } from "@/utils/dom"
import { QueryEngine, QUERY_ENGINE_TYPES } from "@/utils/types"
import { useQuery } from "@tanstack/react-query"
import dayjs from "dayjs"
import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

interface QueryEnginesProps {
  token: string
}

const MAX_ENGINE_DISPLAY = 20

const QueryEngines: React.FC<QueryEnginesProps> = ({ token }) => {
  const [engines, setQueryEngines] = useState<QueryEngine[]>([])

  const { data: queryEngines, isLoading, error: enginesError } = useQuery(
    ["fetchEngines"], 
    fetchAllEngines(token)
  )

  useEffect(() => {
    setQueryEngines(queryEngines ?? [])
  }, [queryEngines])

  if (isLoading) return <Loading />

  return (
    <div className="overflow-x-auto custom-scrollbar">
      <table className="table-lg table-zebra table w-full">
        {/* head */}
        <thead>
          <tr className="text-left">
            <th>Engine Name</th>
            <th>Engine Type</th>
            <th>Data URL</th>
            <th>Created At</th>
          </tr>
        </thead>
        <tbody className="opacity-80">
          {engines
            .sort((a, b) => (b.created_time > a.created_time ? 1 : -1))
            .slice(0, MAX_ENGINE_DISPLAY)
            .map((engine, i) => (
              <tr
                key={engine.id}
                className={classNames(
                  "text-sm lg:text-base",
                  i % 2 === 0 ? "bg-base-200" : "bg-base-100",
                )}
              >
                <td className="text-sm lg:min-w-60">
                  <Link
                    to={`/aiquery`}
                    className="text-primary text-sm transition hover:underline lg:text-base"
                  >
                    {engine.name}
                  </Link>
                </td>
                <td className="text-xs md:text-sm lg:min-w-46 lg:text-base">
                  {QUERY_ENGINE_TYPES[engine.query_engine_type]}
                </td>
                <td className="text-xs md:text-sm lg:min-w-56 lg:text-base">
                  {engine.doc_url}
                </td>
                <td className="text-xs md:text-sm lg:min-w-56 lg:text-base">
                  {dayjs(engine.created_time).format("MMM D • h:mm A")}
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  )
}

export default QueryEngines
