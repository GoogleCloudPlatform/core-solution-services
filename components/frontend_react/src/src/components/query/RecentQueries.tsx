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

import React, { useEffect } from "react"
import { fetchQueryHistory } from "@/utils/api"
import { useQuery } from "@tanstack/react-query"
import { useQueryParams } from "@/utils/routing"
import dayjs from "dayjs"
import { Link } from "react-router-dom"
import Loading from "@/navigation/Loading"

interface RecentQueriesProps {
  token: string
}

const QUERY_DISPLAY_LIMIT = 4

const RecentQueries: React.FC<RecentQueriesProps> = ({ token }) => {
  const {
    isLoading,
    error,
    refetch,
    data: queryHistory,
  } = useQuery(["QueryHistory"], fetchQueryHistory(token))

  const params = useQueryParams()
  const currQueryId = params.get("query_id")

  // Force fetch on query ID change to display newly created query
  useEffect(() => {
    if (currQueryId) {
      refetch()
    }
  }, [currQueryId])

  if (isLoading) return <></>
  if (error) return <></>
  if (!queryHistory?.length) return <Loading />

  const recentQueries = queryHistory
    .sort((a, b) => (b.created_time > a.created_time ? 1 : -1))
    .slice(0, QUERY_DISPLAY_LIMIT)

  return (
    <div className="border-primary-content mt-2 border-t p-2 py-3">
      <div className="text-primary-content pb-3 font-semibold">
        Recent Queries
      </div>

      <div className="flex flex-col gap-4">
        {recentQueries.map((query) => (
          <Link
            key={query.id}
            className="border-primary-content text-primary-content hover:bg-primary-active flex cursor-pointer flex-col gap-1 rounded border-l-2 border-opacity-60 pl-2 opacity-80 transition"
            to={`/aiquery?query_id=${query.id}`}
          >
            <div className="text-md truncate">{query.prompt}</div>
            <div className="text-xs">
              {dayjs(query.created_time).format("MMM D, YYYY • h:mm A")}
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default RecentQueries
