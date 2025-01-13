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

import Loading from "@/navigation/Loading"
import { classNames } from "@/utils/dom"
import {
  CheckCircleIcon,
  CloudArrowUpIcon,
  ExclamationCircleIcon,
} from "@heroicons/react/24/outline"
import { useState } from "react"

const defaultAccept = "image/*,.pdf,.docx,.doc,.ppt,.xls,.xlsx,.mp3,.mp4"

const DocumentUpload = ({
  type,
  label,
  handleFiles,
  accept,
  multiple,
}: {
  type: string
  label: string
  handleFiles: Function
  accept?: string
  multiple?: boolean
}) => {
  const [uploading, setUploading] = useState(false)
  const [uploaded, setUploaded] = useState(false)
  const [failed, setFailed] = useState(false)
  const [filesLabel, setFilesLabel] = useState<string | null>(null)
  multiple = multiple ?? false

  const onChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    setFailed(false)
    setUploaded(false)
    setUploading(true)
    if (files === null || files.length < 1) {
      setUploading(false)
      setFilesLabel(null)
      return
    }

    try {
      await handleFiles({ files, type, label })
      setUploaded(true)

      setFilesLabel(
        files.length > 1
          ? `${files.length} files added`
          : files[0]?.name ?? "File added",
      )
    } catch (error) {
      setFailed(true)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="group flex w-full items-center justify-center">
      <label
        htmlFor={type}
        className={classNames(
          "flex h-32 w-full cursor-pointer flex-col rounded-md border-4 border-dashed transition",
          failed
            ? "border-error"
            : uploaded
              ? "border-success"
              : "text-faint group-hover:text-normal border-base-300",
        )}
      >
        <div className="flex flex-col items-center justify-center pt-7">
          {failed ? (
            <ExclamationCircleIcon className="h-10 text-error transition" />
          ) : uploaded ? (
            <CheckCircleIcon className="h-10 text-success transition" />
          ) : uploading ? (
            <Loading />
          ) : (
            <CloudArrowUpIcon className="h-7 text-base" />
          )}
          <p
            className={classNames(
              "text-sm",
              failed
                ? "text-error"
                : uploaded
                  ? "text-success"
                  : "text-base-content",
              "pt-1 text-lg font-semibold",
            )}
          >
            {filesLabel || label}
          </p>
        </div>
        <input
          id={type}
          type="file"
          name={type}
          className="w-full cursor-pointer opacity-0"
          accept={accept || defaultAccept}
          onChange={onChange}
          multiple={multiple}
          disabled={uploading}
        />
      </label>
    </div>
  )
}

export default DocumentUpload
