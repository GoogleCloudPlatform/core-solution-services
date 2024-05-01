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
