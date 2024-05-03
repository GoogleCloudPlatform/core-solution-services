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

import { classNames } from "@/utils/dom"
import { ReactNode } from "react"

interface HeaderProps {
  className?: string
  children: ReactNode
}

const Header: React.FC<HeaderProps> = (props) => {
  return (
    <div
      className={classNames(
        props.className ?? "",
        "text-3xl font-semibold opacity-80",
      )}
    >
      {props.children}
    </div>
  )
}

export default Header
