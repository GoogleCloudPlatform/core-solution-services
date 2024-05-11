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
import { fetchQueryHistory } from "@/utils/api"
import { fallBackQueries } from "@/utils/data"
import { classNames } from "@/utils/dom"
import { Query } from "@/utils/types"
import { useQuery } from "@tanstack/react-query"
import dayjs from "dayjs"
import { useEffect, useState } from "react"
import { Link } from "react-router-dom"

interface QueriesProps {
  token: string
}

const MAX_QUERY_DISPLAY = 20

const Queries: React.FC<QueriesProps> = ({ token }) => {
  const [queries, setQueries] = useState<Query[]>([])

  const { isLoading, data: queryHistory } = useQuery(
    ["QueryHistory"],
    fetchQueryHistory(token),
  )

  useEffect(() => {
    setQueries(queryHistory ?? fallBackQueries)
  }, [queryHistory])

  if (isLoading) return <Loading />

  return (
    <div className="overflow-x-auto custom-scrollbar">
      <table className="table-lg table-zebra table w-full">
        {/* head */}
        <thead>
          <tr className="text-left">
            <th>Initial chat prompt</th>
            <th>Created at</th>
          </tr>
        </thead>
        <tbody className="opacity-80">
          {queries
            .sort((a, b) => (b.created_time > a.created_time ? 1 : -1))
            .slice(0, MAX_QUERY_DISPLAY)
            .map((query, i) => (
              <tr
                key={query.id}
                className={classNames(
                  "text-sm lg:text-base",
                  i % 2 === 0 ? "bg-base-200" : "bg-base-100",
                )}
              >
                <td className="text-sm lg:text-base">
                  <Link
                    to={`/aiquery?query_id=${query.id}`}
                    className="text-primary text-sm transition hover:underline lg:text-base"
                  >
                    {query.prompt}
                  </Link>
                </td>
                <td className="text-xs md:text-sm lg:min-w-56 lg:text-base">
                  {dayjs(query.created_time).format("MMM D, YYYY • h:mm A")}
                </td>
              </tr>
            ))}
        </tbody>
      </table>
    </div>
  )
}

export default Queries
