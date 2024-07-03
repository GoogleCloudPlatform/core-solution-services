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
import { useEffect, useState } from "react"

interface TeamListFieldProps {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const TeamListField: React.FC<TeamListFieldProps> = ({
  variable,
  formikProps,
}) => {
  const teamFormatDefault = {
    name: "",
    email: "",
    image: "",
    ldap: "",
  }
  const [teamFormat, setTeamFormat] = useState(teamFormatDefault)
  const { values, setFieldValue } = formikProps

  const inputHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.name === "teamName") {
      teamFormat.name = event.target.value
    }
    if (event.target.name === "teamEmail") {
      teamFormat.email = event.target.value
    }
    if (event.target.name === "teamImageLink") {
      teamFormat.image = event.target.value
    }
    if (event.target.name === "teamLdap") {
      teamFormat.ldap = event.target.value
    }
    setFieldValue(variable.name, [teamFormat])
  }

  useEffect(() => {
    if (values[variable.name] !== undefined) {
      if (values[variable.name].length) {
        setTeamFormat(values[variable.name][0])
      }
    } else {
      setTeamFormat(teamFormatDefault)
    }
  }, [values[variable.name]])

  return (
    <>
      {teamFormat && (
        <FormikProvider value={formikProps}>
          <div className="form-control" key={variable.name}>
            <div className="mt-1 w-full justify-between sm:flex sm:gap-2">
              <Field
                name="teamName"
                placeholder="Name"
                className="input input-bordered input-sm w-full"
                onChange={inputHandler}
                value={teamFormat.name}
              />
              <Field
                name="teamEmail"
                placeholder="Email"
                className="input input-bordered input-sm w-full mt-2 sm:mt-0"
                onChange={inputHandler}
                value={teamFormat.email}
              />
            </div>
            <div className="mt-2 w-full justify-between sm:flex sm:gap-2">
              <Field
                name="teamImageLink"
                placeholder="Profile Image"
                className="input input-bordered input-sm w-full"
                onChange={inputHandler}
                value={teamFormat.image}
              />
              <Field
                name="teamLdap"
                placeholder="Ldap"
                className="input input-bordered input-sm w-full mt-2 sm:mt-0"
                onChange={inputHandler}
                value={teamFormat.ldap}
              />
            </div>

            <div className="text-faint mt-1 text-sm">
              {variable.description}
            </div>
          </div>
        </FormikProvider>
      )}
    </>
  )
}

export default TeamListField
