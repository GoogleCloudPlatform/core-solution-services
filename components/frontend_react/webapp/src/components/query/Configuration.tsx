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
import { fetchAllChatModels, fetchAllEngines } from "@/utils/api"
import { useQuery } from "@tanstack/react-query"
import Loading from "@/navigation/Loading"
import { useConfig } from "@/contexts/configContext"

interface ConfigurationProps {
  token: string
}

const QueryConfiguration: React.FC<ConfigurationProps> = ({ token }) => {
  const { data: engineList, isLoading: enginesLoading, error: enginesError } = useQuery(["fetchEngines"], fetchAllEngines(token))
  const { data: modelList, isLoading: modelsLoading, error: modelsError } = useQuery(["fetchModels"], fetchAllChatModels(token))

  const { selectedModel, setSelectedModel, selectedEngine, setSelectedEngine } = useConfig()

  useEffect(() => {
    if (engineList && engineList.length > 0 && !selectedEngine) {
      setSelectedEngine(engineList[0].id)
    }
  }, [engineList, selectedEngine, setSelectedEngine])

  if (enginesError || modelsError) return <></>
  if (enginesLoading || modelsLoading) {
    return <Loading />
  }
  
  return (
    <div className="border-primary-content mt-2 border-t p-2 py-3">
      <div className="text-primary-content pb-3 font-semibold">
        Configuration
      </div>

      <div>
        <label htmlFor="model-select" className="label w-fit pt-0"><span className="label-text text-primary-content">Model:</span></label>
        <select
          id="model-select"
          className="select select-sm w-full border-none outline-none focus:outline-none h-10"
          onChange={(e) => setSelectedModel(e.target.value)}
          value={selectedModel}
        >
          {modelList &&
            modelList.map((modelOpt) => <option key={modelOpt} value={modelOpt}>{modelOpt}</option>)
          }
        </select>
        <label htmlFor="engine-select" className="label w-fit pt-3"><span className="label-text text-primary-content">Query Engine:</span></label>
        <select
          id="engine-select"
          className="select select-sm w-full border-none outline-none focus:outline-none h-10"
          onChange={(e) => setSelectedEngine(e.target.value)}
          value={selectedEngine}
        >
          {engineList &&
            engineList.map((engine) => <option key={engine.id} value={engine.id}>{engine.name}</option>)
          }
        </select>
      </div>
    </div>
  )
}

export default QueryConfiguration
