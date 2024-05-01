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
import {
  DemoPriorities,
  CloudProducts,
  UseCases,
  SalesTags,
  AccreditationStatus,
} from "@gps-demos/demo-portal-types"
import QueryEngineFormFields from "@/components/forms/QueryEngineFormFields"
import Link from "next/link"
import { QueryEngine, IFormValidationData, IFormVariable } from "@/utils/types"
import { formValidationSchema, initialFormikValues } from "@/utils/forms"

interface QueryEngineFormProps {
  queryEngine: QueryEngine | null
  onSubmit: Function
  onSuccess: Function
  onFailure: Function
  token: string
  currentVarsData: IFormVariable[]
}

const QueryEngineForm: React.FunctionComponent<QueryEngineFormProps> = ({
  onSubmit,
  onSuccess,
  onFailure,
  queryEngine,
  token,
  currentVarsData,
}) => {
  const [submitting, setSubmitting] = useState(false)
  const [qEngineInitialFormat, setDemoInitialFormat] = useState({})

  const defaultValues = initialFormikValues(currentVarsData)

  const handleFiles = (_files: FileList, _uploadVariable: string) => {
    //handle file upload if required in future
  }

  const handleSubmit = async (values: Record<string, any>) => {
    const priority =
      values.priority ?? DemoPriorities[DemoPriorities.length - 1] // Default to lowest priority

    values = {
      ...values,
      // @ts-ignore
      priority: parseInt(priority),
    }

    const {
      cloudProducts,
      useCases,
      salesTags,
      accreditationStatus,
      filesfileHideInPDP,
      ...restValues
    } = values

    const tags = cloudProducts
      .concat(useCases)
      .concat(salesTags)
      .concat(accreditationStatus)

    const payloadData: IDemo | Record<string, any> = Object.assign(
      {},
      restValues,
      { tags: tags },
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
      const { tags, ...restDemoValues } = queryEngine

      const qEngineInitialFormating = Object.assign(
        {},
        restDemoValues,
        { cloudProducts: cloudProducts },
        { useCases: useCases },
        { salesTags: salesTags },
        { accreditationStatus: accreditationStatus },
      )
      setDemoInitialFormat(qEngineInitialFormating)
    }
  }, [demo])

  const initialValues = Object.assign({}, defaultValues, qEngineInitialFormat)

  const formValidationData: IFormValidationData =
    formValidationSchema(currentVarsData)

  const formik = useFormik({
    initialValues: initialValues,
    enableReinitialize: true,
    validateOnMount: true,
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
            <DemoFormFields
              variableList={currentVarsData}
              formikProps={formik}
              demo={demo}
              token={token}
              handleFiles={handleFiles}
            />
          ) : (
            <></>
          )}

          <div className="mt-2 flex justify-between">
            <Link href="#">
              <button
                className="btn btn-outline btn-sm"
                onClick={() => window.history.go(-1)}
              >
                Back
              </button>
            </Link>
            <button
              className="btn btn-primary btn-sm"
              type="submit"
              disabled={Boolean(
                submitting || Object.keys(formik.errors).length,
              )}
            >
              {demo?.id ? "Update" : "Submit"}
            </button>
          </div>
        </Form>
      </FormikProvider>
    </div>
  )
}

export default QueryEngineForm
