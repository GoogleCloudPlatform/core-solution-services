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

import React, { useState } from "react"
import { classNames } from "@/utils/dom"
import { useNavigate } from "react-router-dom"
import { useQueryParams } from "@/utils/routing"
import { userStore } from "@/store"
import QueryEngineEdit from "@/routes/QueryEngineEdit"
import QueryEngineJobs from "@/routes/QueryEngineJobs"
//import QueryEngineSimple from "@/routes/QueryEngineSimple"

// TODO: implement query engine from uploads
//
//enum TAB {
//  QUERY_ENGINE_SIMPLE = "Query Engine Simple",
//  QUERY_ENGINE = "Query Engine Advanced",
//  QUERY_ENGINE_JOBS = "Query Engine Jobs",
//}

enum TAB {
  QUERY_ENGINE = "Query Engine",
  QUERY_ENGINE_JOBS = "Query Engine Jobs",
}

interface IQueryEngineAdminProps {
  token: string
}

const QueryEngineAdmin: React.FC<IQueryEngineAdminProps> = ({ token }) => {

  const isAdmin = true // TODO: userStore((state) => state.isAdmin)

  const [activeTab, setActiveTab] = useState<TAB>(TAB.QUERY_ENGINE)

  const params = useQueryParams()
  const id = params.get("qe_id")
  const navigate = useNavigate()
  
  const renderTab = (tab: TAB) => {
    return (
      <a
        role="tab"
        data-testid={tab}
        className={classNames(
          "tab px-6 md:px-12 font-bold",
          activeTab == tab ? "border-b-2 border-primary text-base-content" : "",
        )}
        onClick={(e) => {
          e.preventDefault()
          setActiveTab(tab)
        }}
      >
        {tab}
      </a>
    )
  }

  return (
    <div className="mb-4 mt-2 rounded-lg border border-base-300 bg-base-100 p-4 text-sm">
      <div className="tabs">
        //<div>{renderTab(TAB.QUERY_ENGINE_SIMPLE)}</div>
        <div>{renderTab(TAB.QUERY_ENGINE)}</div>
        <div>{renderTab(TAB.QUERY_ENGINE_JOBS)}</div>
      </div>
      <div className="p-0">
      {/*
        {activeTab === TAB.QUERY_ENGINE_SIMPLE && (
          <div className="border-t border-base-300 p-2">
            <QueryEngineSimple token={token!} />
          </div>
        )}
      */}
        {activeTab === TAB.QUERY_ENGINE && (
          <div className="border-t border-base-300 p-2">
            <QueryEngineEdit token={token!} />
          </div>
        )}

        {activeTab === TAB.QUERY_ENGINE_JOBS && (
          <div className="border-t border-base-300 p-2">
            <QueryEngineJobs token={token!} />
          </div>
        )}
      </div>
    </div>
  )
}

export default QueryEngineAdmin
