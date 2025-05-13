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

import { classNames } from "../../src/lib/dom"
import { CSSProperties } from "react"

const outerStyles: CSSProperties = {
  minHeight: "100%",
  minWidth: "100%",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
}

interface LoadingProps {
  className?: string
}

const Loading: React.FC<LoadingProps> = ({ className }) => {
  return (
    <div style={outerStyles}>
      <span
        className={classNames(
          "loading loading-ring loading-lg text-primary",
          className || "",
        )}
      ></span>
    </div>
  )
}

export default Loading
