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
import { AppConfig } from "@/utils/AppConfig"
import { isEmailAuthorized } from "@/utils/auth"
import { classNames } from "@/utils/dom"
import { auth, googleProvider, logEvent } from "@/utils/firebase"
import { IAuthProvider } from "@/utils/types"
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signInWithPopup,
} from "firebase/auth"
import { ErrorMessage, Field, Form, Formik } from "formik"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { Link, useNavigate } from "react-router-dom"
import { object, string } from "yup"

interface SignInFormProps {
  authOptions: IAuthProvider[]
}

const passwordSchema = object({
  email: string().required("Email is required").email(),
  password: string()
    .required("Password is required")
    .min(8, "Must be at least 8 characters"),
})

type PasswordFields = {
  email: string
  password: string
}

const defaultPasswordFormValues: PasswordFields = {
  email: "",
  password: "",
}

const SignInForm: React.FunctionComponent<SignInFormProps> = ({
  authOptions,
}) => {
  const { t: ts } = useTranslation("auth")
  const navigate = useNavigate()

  const [submittingGoogle, setSubmittingGoogle] = useState(false)
  const [submittingPassword, setSubmittingPassword] = useState(false)
  const [authError, setAuthError] = useState<string | null>(null)

  const AUTH_ERROR_MESSAGES = {
    "auth/operation-not-allowed":
      "Ask your developer to enable this signin method.",
    "auth/wrong-password":
      "Wrong user/password combination, or you previously used a different signin method.",
    "auth/user-not-found": "",
    default: "Uh oh! Something went wrong.",
  }

  const signInWithGoogle = async () => {
    setAuthError(null)
    setSubmittingGoogle(true)

    try {
      const { user } = await signInWithPopup(auth, googleProvider)
      if (!user.email) {
        throw new Error("User is missing email")
      }

      if (!isEmailAuthorized(AppConfig.authorizedDomains, user.email)) {
        const err = `Domain is not authorized: ${user.email.split("@")[1]}`
        await auth.signOut()
        setAuthError(err)
        throw new Error(err)
      }

      logEvent("login", { method: "Google" })
      navigate("/")
      return
    } catch (error) {
      console.error(error)
      setSubmittingGoogle(false)
    }
  }

  const signInWithPassword = ({ email, password }: PasswordFields) => {
    setAuthError(null)
    setSubmittingPassword(true)

    signInWithEmailAndPassword(auth, email, password)
      .catch((error) => {
        if (error.code === "auth/user-not-found") {
          // User has not been created
          return createUserWithEmailAndPassword(auth, email, password)
        }
        throw error
      })
      .then(() => {
        logEvent("login", { method: "Email" })
        navigate("/")
        return
      })
      .catch((error) => {
        setAuthError(
          // @ts-ignore
          AUTH_ERROR_MESSAGES[error?.code || "default"] ??
            AUTH_ERROR_MESSAGES.default,
        )
        console.error(error)
        setSubmittingPassword(false)
      })
  }

  const renderGoogle = () => (
    <button
      onClick={signInWithGoogle}
      disabled={submittingGoogle}
      className={classNames(
        "btn border-base-300 bg-base-100 w-full shadow-lg",
        submittingGoogle
          ? "text-base-content cursor-not-allowed"
          : "hover:border-primary hover:bg-base-100 cursor-pointer",
      )}
    >
      {submittingGoogle ? (
        <div className="mr-4">
          <Loading />
        </div>
      ) : (
        <img
          className="mr-4 h-8 w-auto"
          src="/assets/images/google.png"
          alt="Google"
        />
      )}
      <div className="text-base-content font-semibold normal-case">
        {ts("auth.signin-google")}
      </div>
    </button>
  )

  // @ts-expect-error
  const renderPassword = () => (
    <div>
      <div className="relative mb-2 mt-10 flex justify-center">
        <div className="border-base-300 absolute top-1/2 w-full border-b"></div>
        <div className="text-faint bg-base-100 z-10 px-4">
          {ts("auth.signin-password")}
        </div>
      </div>

      <Formik
        initialValues={defaultPasswordFormValues}
        validationSchema={passwordSchema}
        onSubmit={signInWithPassword}
      >
        <Form>
          <div className="form-control">
            <label htmlFor="email" className="text-left">
              {ts("auth.email")}
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

          <div className="form-control">
            <label htmlFor="password" className="text-left">
              {ts("auth.password")}
            </label>
            <Field
              type="password"
              id="password"
              name="password"
              className="input"
              autoComplete="current-password"
            />
            <div className="invalid-feedback text-left">
              <ErrorMessage name="password" />
            </div>
          </div>

          <div className="flex justify-between">
            <Link to={"/password-reset"}>
              <a className="text-sm">Forgot your password?</a>
            </Link>

            <button
              className="btn-primary btn"
              type="submit"
              disabled={submittingPassword}
            >
              {submittingPassword ? (
                <div className="flex w-20 items-center justify-center">
                  <Loading />
                </div>
              ) : (
                <div className="flex w-20 items-center justify-center">
                  {ts("auth.signin")}
                  <div className="i-heroicons-arrow-right ml-2 h-4 w-4" />
                </div>
              )}
            </button>
          </div>
        </Form>
      </Formik>
    </div>
  )

  return (
    <div className="grid grid-cols-1 gap-y-8">
      {authError && (
        <div className="border-error bg-error text-error my-4 rounded-lg border bg-opacity-10 px-2 py-1">
          {authError}
        </div>
      )}
      {authOptions.includes("google") ? renderGoogle() : <></>}
      {/*{authOptions.includes("password") ? renderPassword() : <></>}*/}
    </div>
  )
}

export default SignInForm
