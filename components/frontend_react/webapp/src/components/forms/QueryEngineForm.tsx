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

import { useState, useEffect } from "react"
import { Form, useFormik, FormikProvider } from "formik"
import FormFields from "@/components/forms/FormFields"
import { QueryEngine } from "@/utils/types"
import { Link } from "react-router-dom"
import { IFormValidationData, IFormVariable } from "@/utils/types"
import { IQueryEngine } from "@/utils/models"
import { formValidationSchema, initialFormikValues } from "@/utils/forms"
import { toBase64 } from "@/utils/api"
import * as yup from "yup"

interface QueryEngineFormProps {
  queryEngine: IQueryEngine | null
  onSubmit: Function
  onSuccess: Function
  onFailure: Function
  currentVarsData: IFormVariable[]
}

const QueryEngineForm: React.FunctionComponent<QueryEngineFormProps> = ({
  queryEngine,
  onSubmit,
  onSuccess,
  onFailure,
  currentVarsData,
}) => {
  const [submitting, setSubmitting] = useState(false)
  const [qEngineInitialFormat, setQueryEngineInitialFormat] = useState({})
  const [queryEngineFiles, setQueryEngineFiles] = useState<FileList | null>()
  const defaultValues = initialFormikValues(currentVarsData)

  const handleFiles = (files: FileList | null, _: any) => {
    setQueryEngineFiles(files)
  }

  currentVarsData = currentVarsData.map(
    (entry) => {
      switch (entry.name) {
        case "doc_url":
          return { ...entry, required: !Boolean(queryEngineFiles?.length) }
        default:
          return entry
      }
    })

  const handleSubmit = async (values: Record<string, any>) => {
    const { archived_at_timestamp, archived_by, created_by, created_time, deleted_at_timestamp,
      deleted_by, id, last_modified_by, last_modified_time, ...restValues } = values
    if (queryEngineFiles?.length) {
      restValues['documents'] = []
      for (const document of queryEngineFiles) {
        restValues['documents'].push({
          name: document.name,
          b64: await toBase64(document)
        })
      }
    }
    const payloadData: QueryEngine | Record<string, any> = Object.assign(
      {},
      restValues,
    )

    try {
      setSubmitting(true)
      const result = await onSubmit(payloadData)
      await onSuccess(result)
    } catch (error) {
      await onFailure(error)
    } finally {
      setSubmitting(false)
    }
  }

  useEffect(() => {
    if (queryEngine && queryEngine !== null) {
      const { archived_at_timestamp, archived_by, created_by, created_time, deleted_at_timestamp,
        deleted_by, id, last_modified_by, last_modified_time, ...restQEValues } = queryEngine

      const qEngineInitialFormatting = Object.assign(
        {},
        restQEValues,
      )
      setQueryEngineInitialFormat(qEngineInitialFormatting)
    }
  }, [queryEngine])

  const initialValues = Object.assign({}, defaultValues, qEngineInitialFormat)

  const validationSettings = {
    name: yup
      .string()
      .max(32, "Query Engine names must be less than or equal to 32 chars")
      .matches("^[a-zA-Z0-9][\w\s-]*[a-zA-Z0-9]$", "Invalid query engine name.  May contain alphanumerics, dashes or spaces.")
  }
  const formValidationData: IFormValidationData =
    formValidationSchema(currentVarsData, validationSettings)

  const formik = useFormik({
    initialValues: initialValues,
    enableReinitialize: true,
    validateOnMount: true,
    validateOnChange: true,
    validationSchema: formValidationData,
    onSubmit: async (values) => {
      await handleSubmit(values)
    },
  })

  return (
    <div className="w-full">
      <FormikProvider value={formik}>
        <Form spellCheck="true">
          {currentVarsData ? (
            <FormFields
              variableList={currentVarsData}
              formikProps={formik}
              handleFiles={handleFiles}
            />
          ) : (
            <></>
          )}

          <div className="mt-2 flex justify-between">
            <Link href="#">
              <button
                className="btn btn-outline btn-sm"
                onClick={() => { formik.resetForm(); handleFiles(null, null) }}
              >
                Clear
              </button>
            </Link>
            <button
              className="btn btn-primary btn-sm"
              type="submit"
              disabled={Boolean(
                submitting || Object.keys(formik.errors).length,
              )}
            >
              {queryEngine?.id ? "Update" : "Submit"}
            </button>
          </div>
        </Form>
      </FormikProvider>
    </div>
  )
}

export default QueryEngineForm
