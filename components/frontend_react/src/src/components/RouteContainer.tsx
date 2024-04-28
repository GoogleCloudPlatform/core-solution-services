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

import React from "react"

interface RouteContainerProps {
  children: React.ReactNode
}

const RouteContainer: React.FC<RouteContainerProps> = ({ children }) => {
  return (
    <div
      className="flex-grow px-4 py-2 md:px-6 lg:px-8"
      data-testid="route-container"
    >
      <div className="mx-auto max-w-screen-lg">{children}</div>
    </div>
  )
}

export default RouteContainer
