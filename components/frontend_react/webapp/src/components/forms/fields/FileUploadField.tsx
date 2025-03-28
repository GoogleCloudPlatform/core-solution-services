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

import { Field, FormikContextType, FormikProvider } from "formik"

import { IFormVariable } from "@/utils/types"

import FieldErrorMessage from "@/components/forms/FieldErrorMessage"
import DocumentUpload from "@/components/DocumentUpload"
import {
  downloadFile,
  fileNameByPath,
} from "@/utils/forms"
import { XMarkIcon } from "@heroicons/react/24/outline"
import { useState } from "react"
import DeleteFilesModal from "@/components/DeleteFilesModal"

interface IFileUploadFieldProps {
  variable: IFormVariable
  formikProps: FormikContextType<any>
  handleFilesUpload: Function
}

type IfileFormat = {
  fileName: string | null | undefined
  fileURL: string
  fieldName: string
}

const FileUploadField: React.FC<IFileUploadFieldProps> = ({
  variable,
  formikProps,
  handleFilesUpload,
}) => {
  const [modal, setModal] = useState(false)
  const [fileData, setFileData] = useState<IfileFormat | null>(null)
  const { values } = formikProps

  //@ts-ignore
  const getUpdatedFiles = values[variable.name]

  const fileNameContains: IfileFormat[] = []
  if (getUpdatedFiles) {
    if (Array.isArray(getUpdatedFiles)) {
      getUpdatedFiles.forEach(async (value: string) => {
        const fileName = fileNameByPath(value)
        const supportingFileObj = {
          fileName: fileName,
          fileURL: value,
          fieldName: variable.name,
        }
        if (fileName) fileNameContains.push(supportingFileObj)
      })
    } else {
      const singleFileName = fileNameByPath(getUpdatedFiles)
      const supportingFileObj = {
        fileName: singleFileName,
        fileURL: getUpdatedFiles,
        fieldName: variable.name,
      }
      if (singleFileName && getUpdatedFiles !== singleFileName)
        fileNameContains.push(supportingFileObj)
    }
  }
  const handleFiles = ({ files }: { files: FileList; type: string }) => {
    handleFilesUpload(files, variable)
  }

  const promptFileDelete = (fileData: IfileFormat) => {
    setFileData(fileData)
  }

  const modalClose = (state: boolean) => {
    setModal(state)
  }

  const renderModal = () => (
    <DeleteFilesModal
      fileData={fileData}
      demoId={demo?.id}
      modalClose={modalClose}
    />
  )
  return (
    <FormikProvider value={formikProps}>
      <div className="form-control">
        <DocumentUpload
          label={variable.fileLabel || "files"}
          type={variable.name}
          multiple={variable.multiple || false}
          accept={variable.accept}
          handleFiles={handleFiles}
        />
        <Field
          id={variable.name}
          name={variable.name}
          value={""}
          className="input hidden"
        />

        <FieldErrorMessage variableName={variable.name} />

        <div className="text-faint text-sm">{variable.description}</div>
        {modal ? renderModal() : null}
      </div>
    </FormikProvider>
  )
}

export default FileUploadField
