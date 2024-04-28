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

import { sendPasswordResetEmail } from "firebase/auth"
import { auth } from "@/utils/firebase"

import { ErrorMessage, Formik, Form, Field } from "formik"
import { object, string } from "yup"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link } from "react-router-dom"
import Loading from "@/navigation/Loading"

const emailSchema = object({
  email: string().required("Email is required").email(),
})

type EmailFields = {
  email: string
}

const defaultEmailFields: EmailFields = {
  email: "",
}

interface PasswordResetFormProps {}

const PasswordResetForm: React.FunctionComponent<
  PasswordResetFormProps
> = () => {
  const { t: ts } = useTranslation("signin")
  const [submitting, setSubmitting] = useState(false)
  const [submitted, setSubmitted] = useState(false)

  const resetPassword = async ({ email }: EmailFields) => {
    try {
      setSubmitting(true)
      await sendPasswordResetEmail(auth, email)
      setSubmitted(true)
    } catch (error) {
      console.error(error)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      {submitted ? (
        <div className="alert alert-info mb-2 rounded-lg py-2 font-semibold transition">
          {ts("reset-email-sent")}
        </div>
      ) : (
        <></>
      )}

      <Formik
        initialValues={defaultEmailFields}
        validationSchema={emailSchema}
        onSubmit={resetPassword}
      >
        <Form>
          <div className="form-control">
            <label htmlFor="email" className="text-left">
              {ts("email")}
            </label>
            <Field
              id="email"
              name="email"
              className="input"
              autoComplete="email"
            />
            <div className="invalid-feedback text-left">
              <ErrorMessage name="email" />
            </div>
          </div>

          <div className="flex justify-between">
            <Link to={"/signin"}>
              <a className="text-sm">{ts("back-to-signin")}</a>
            </Link>

            <button
              className="btn btn-primary"
              type="submit"
              disabled={submitting || submitted}
            >
              {submitting ? (
                <div className="flex w-20 items-center justify-center">
                  <Loading />
                </div>
              ) : (
                <div className="flex w-20 items-center justify-center">
                  {ts("reset")}
                  <div className="i-heroicons-arrow-right ml-2 h-4 w-4" />
                </div>
              )}
            </button>
          </div>
        </Form>
      </Formik>
    </div>
  )
}

export default PasswordResetForm
