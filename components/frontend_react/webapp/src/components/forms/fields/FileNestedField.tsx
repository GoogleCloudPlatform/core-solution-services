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

interface FileNestedFieldProps {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const FileNestedField: React.FC<FileNestedFieldProps> = ({
  variable,
  formikProps,
}) => {
  const fileFormatDefault = {
    type: variable.fileType,
    link: {
      name: "",
      href: "",
    },
    description: "",
  }

  const [fileFormat, setFileFormat] = useState(fileFormatDefault)
  const { values, setFieldValue, errors } = formikProps

  const inputHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.name === `${variable.name}fileLink`) {
      fileFormat.link.href = event.target.value
    }
    if (event.target.name === `${variable.name}fileName`) {
      fileFormat.link.name = event.target.value
    }
    if (event.target.name === `${variable.name}fileDescription`) {
      fileFormat.description = event.target.value
    }

    setFieldValue(variable.name, fileFormat.link.href ? fileFormat : {})
  }

  useEffect(() => {
    if (values[variable.name] !== undefined) {
      if (Object.keys(values[variable.name]).length) {
        setFileFormat(values[variable.name])
      }
    } else {
      setFileFormat(fileFormatDefault)
    }
  }, [values[variable.name]])
  return (
    <>
      {fileFormat && (
        <FormikProvider value={formikProps}>
          <div className="form-control" key={variable.name}>
            <div className="mt-1 w-full justify-between sm:flex sm:gap-2">
              <div className="w-full">
                <Field
                  name={`${variable.name}fileLink`}
                  placeholder="File Link"
                  className="input input-bordered input-sm w-full"
                  onChange={inputHandler}
                  value={fileFormat.link.href}
                />
                {
                  //@ts-ignore
                  errors[variable.name]?.link?.href && (
                    <div className="text-error text-xs mt-1">
                      {
                        //@ts-ignore
                        errors[variable.name]?.link?.href
                      }
                    </div>
                  )
                }
              </div>
              <Field
                name={`${variable.name}fileName`}
                placeholder="File Name"
                className="input input-bordered input-sm w-full mt-2 sm:mt-0"
                onChange={inputHandler}
                value={fileFormat.link.name}
              />
            </div>
            <div className="mt-2 flex w-full">
              <Field
                name={`${variable.name}fileDescription`}
                placeholder="File Description"
                component="textarea"
                className="textarea textarea-bordered h-12 w-full"
                onChange={inputHandler}
                value={fileFormat.description}
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

export default FileNestedField
