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
import { QueryReferences } from "@/utils/types"
import Markdown from "react-markdown"
import rehypeRaw from "rehype-raw"

interface ReferencesProps {
  references: QueryReferences[]
}

const References: React.FC<ReferencesProps> = ({ references }) => {
  const dedupList = <T extends Record<string, any>>(items: T[], dedupKey: keyof T): T[] => {
    const map = new Map<string, T>()
    items.forEach(item => {
      const key: string = String(item[dedupKey])
      map.set(key, item)
    })
    return Array.from(map.values())
  }

  const renderCloudStorageUrl = (url: string): string => {
    if (url.startsWith("/b/")) {
      return url
        .replace("/b/", "https://storage.googleapis.com/")
        .replace("/o/", "/")
    }
    if (url.startsWith("gs://"))
      return url.replace("gs://", "https://storage.googleapis.com/")
    return url
  }

  const getLastPathSegment = (urlString: string): string => {
    try {
      const url = new URL(urlString)
      const pathSegments = url.pathname.split('/').filter(Boolean)
      return pathSegments.pop() || url.pathname // Return domain if no segments
    } catch (error) {
      // Handle invalid URL gracefully 
      console.error("Invalid ref URL:", urlString)
      return ''
    }
  }

  const renderLinkTitle = (url: string): string => {
    const decodedUrl = decodeURIComponent(url)

    var basename = decodedUrl.substring(decodedUrl.lastIndexOf('/') + 1)

    // To remove the file extension, uncomment the next line
    // const titleWithoutExtension = basename.replace(/\.[^/.]+$/, "")

    // if the basename doesn't contain a file name, display the last segment of the URL path
    // so for urls like "https://a.com/b/c/" return 'c'
    // for urls like "https://a.com/" return "a.com"
    if (basename.length == 0) {
      basename = getLastPathSegment(decodedUrl)
    }

    return basename
  }

  const truncateText = (text: string, limit: number = 75): string => {
    const words = text.split(/\s+/)
    if (words.length > limit) {
      return words.slice(0, limit).join(" ") + "…"
    }
    return text
  }

  const uniqueReferences = dedupList(references, "chunk_id")

  return (
    <div className="w-full">
      {uniqueReferences.map((ref, index) => (
        <div key={ref.chunk_id} className="mb-3 mr-4">
          <span className="inline-ref">
            <a href={renderCloudStorageUrl(ref.document_url)}
               target="_blank"
               rel="noopener noreferrer"
               className="text-info hover:text-info-content break-all transition-colors mr-1.5">
              {renderLinkTitle(ref.document_url)}:
            </a>
            {ref?.modality === "image" ?
              <img src={renderCloudStorageUrl(ref.chunk_url)} /> :
              // if the modality is not image assume it is text to handle
              // legacy query engines that didn't set a modality
              <Markdown children={truncateText(ref.document_text)} rehypePlugins={[rehypeRaw]} />
            }
          </span>
          <div className={index < uniqueReferences.length - 1 ? "mx-2 pt-3 border-b" : ""} />
        </div>
      ))}
    </div>
  )
}

export default References
