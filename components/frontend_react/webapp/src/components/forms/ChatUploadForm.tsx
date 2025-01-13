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
import { Link } from "react-router-dom"
import { IFormValidationData, IFormVariable } from "@/utils/types"
import { formValidationSchema, initialFormikValues } from "@/utils/forms"

interface ChatUploadFormProps {
  handleFiles: Function
  token: string
  currentVarsData: IFormVariable[]
}

const ChatUploadForm: React.FunctionComponent<ChatUploadFormProps> = ({
  handleFiles,
  token,
  currentVarsData,
}) => {
  const [initialFormat, setInitialFormat] = useState({})
  // This state is used as a key for the form element so the clear butotn
  // can change it to reset everything
  const [resetKey, setResetKey] = useState(1)
  const defaultValues = initialFormikValues(currentVarsData)

  const initialValues = Object.assign({}, defaultValues, initialFormat)

  const formValidationData: IFormValidationData =
    formValidationSchema(currentVarsData)

  const formik = useFormik({
    initialValues: initialValues,
    enableReinitialize: true,
    validateOnMount: true,
    validationSchema: formValidationData,
    onSubmit: null
  })

  return (
    <div className="w-full">
      <FormikProvider value={formik} key={resetKey}>
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
                onClick={() => {
                  formik.resetForm()
                  handleFiles(null, "")
                  setResetKey(resetKey * -1)
                }}
              >
                Clear
              </button>
            </Link>
          </div>
        </Form>
      </FormikProvider>
    </div >
  )
}

export default ChatUploadForm
