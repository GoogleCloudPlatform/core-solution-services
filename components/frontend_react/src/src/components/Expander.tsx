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

import React, { useState, useEffect } from "react"

interface ExpanderProps {
  title: string
  children: React.ReactNode
  initiallyOpen?: boolean
}

const Expander: React.FC<ExpanderProps> = ({ title, children, initiallyOpen = false }) => {
  const [isOpen, setIsOpen] = useState(initiallyOpen)

  // Effect to handle external changes to initiallyOpen, if needed
  useEffect(() => {
    setIsOpen(initiallyOpen)
  }, [initiallyOpen])

  const toggleCollapse = () => {
    setIsOpen(!isOpen)
  }

  return (
    <div
      tabIndex={0}
      className={`collapse-arrow bg-base-100 collapse rounded-lg border-none ${isOpen ? 'collapse-open' : 'collapse-close'}`}
    >
      <div
        className="collapse-title w-fit font-medium cursor-pointer select-none hover:text-base-content/75 transition-colors"
        onClick={toggleCollapse}
      >
        {title}
      </div>
      {isOpen && (
        <div className="collapse-content text-sm cursor-default">
          {children}
        </div>
      )}
    </div>
  )
}

export default Expander
