/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import React, { useRef, useEffect } from "react"
import QueryInput from "./QueryInput"
import Expander from "@/components/Expander"
import References from "@/components/query/References"
import { QueryContents } from "@/utils/types"
import Markdown from "react-markdown"
import rehypeRaw from "rehype-raw"

interface QueryWindowProps {
  onSubmit: (message: string) => void
  messages: QueryContents[]
  activeJob: boolean
}

const QueryWindow: React.FC<QueryWindowProps> = ({ onSubmit, messages, activeJob }) => {
  let index = 0
  const renderQuery = (message: QueryContents) => {
    if (message.HumanQuestion) {
      return (
        <div key={index++}>
          <div className="flex items-center gap-6 pb-7 mx-2">
            <div className="i-material-symbols-face-outline color-info h-8 w-8 shrink-0 self-start"/>
            <div>
              {message.HumanQuestion}
            </div>
          </div>
        </div>
      )
    } else if (message.AIResponse) {
      return (
        <div key={index++}>
          <div className={`flex items-center gap-6 mx-2 ${message.AIReferences ? 'pb-2' : 'pb-7'}`}>
            <div className="i-logos-google-bard-icon h-8 w-8 shrink-0 self-start"/>
            <div>
              <Markdown children={message.AIResponse} rehypePlugins={[rehypeRaw]} />
            </div>
          </div>
          {message.AIReferences &&
            <div className="ml-12 mb-2">
              <Expander title={"References"}>
                <References references={message.AIReferences} />
              </Expander>
            </div>
          }
        </div>
      )
    } else if (message.AIReferences) {
      return (
        <div key={index++} className="ml-12 mb-2">
          <Expander title={"References"}>
            <References references={message.AIReferences} />
          </Expander>
        </div>
      )
    } else {
      return
    }
  }

  const endOfMessagesRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Scroll into view when activeJob is false
    if (activeJob) {
      endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" })
    }
    if (!messages[messages.length - 1].HumanQuestion && !activeJob) {
      endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" })
    }
  }, [messages, activeJob])

  return (
    <div className="flex flex-grow flex-col justify-between max-w-4xl">
      <div className="text-md flex-grow overflow-y-auto custom-scrollbar max-h-[calc(100vh-17.3rem)]">
        {messages.map(renderQuery)}
        {activeJob && (
          <div className="flex items-center gap-6 pb-7 pt-2 mx-2">
            <div className="i-logos-google-bard-icon h-8 w-8 shrink-0 self-start loader ease-linear"/>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>
      <QueryInput onSubmit={onSubmit} activeJob={activeJob} />
    </div>
  )
}

export default QueryWindow