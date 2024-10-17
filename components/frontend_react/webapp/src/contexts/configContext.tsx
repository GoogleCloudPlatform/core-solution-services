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

import { createContext, useContext, useState, ReactNode } from "react"

interface ConfigContextType {
  selectedModel: string
  setSelectedModel: (model: string) => void
  selectedEngine: string
  setSelectedEngine: (engine: string) => void
}

const ConfigContext = createContext<ConfigContextType>({
  selectedModel: "VertexAI-Chat",
  setSelectedModel: () => {},
  selectedEngine: "",
  setSelectedEngine: () => {}
})

export const useConfig = () => useContext(ConfigContext)

interface ConfigProviderProps {
  children: ReactNode
}

export const ConfigProvider = ({ children }: ConfigProviderProps) => {
  const [selectedModel, setSelectedModel] = useState("VertexAI-Chat")
  const [selectedEngine, setSelectedEngine] = useState("")

  const value = {
    selectedModel,
    setSelectedModel,
    selectedEngine,
    setSelectedEngine
  }

  return (
    <ConfigContext.Provider value={value}>
      {children}
    </ConfigContext.Provider>
  )
}
