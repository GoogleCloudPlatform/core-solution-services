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

import { Field, FieldArray, FormikContextType, FormikProvider } from "formik"
import { PlusIcon, XMarkIcon } from "@heroicons/react/24/outline"
import { useState } from "react"

import { IFormVariable } from "@/utils/types"

interface PersonaListField {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}
type IObjKeyPair = {
  name: string
  description: string
}

const PersonaListField: React.FC<PersonaListField> = ({
  variable,
  formikProps,
}) => {
  const mapFormatDefault: IObjKeyPair = {
    name: "",
    description: "",
  }
  const [mapFormat] = useState<IObjKeyPair>(mapFormatDefault)

  const inputHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.name === "map_set_key") {
      mapFormat.name = event.target.value
    }
    if (event.target.name === "map_set_value") {
      mapFormat.description = event.target.value
    }
  }

  const onSetKeyValue =
    (FieldArrayProps: any) => (event: React.MouseEvent<HTMLButtonElement>) => {
      event.preventDefault()
      const { push } = FieldArrayProps

      if (mapFormat.name && mapFormat.description) {
        push(mapFormat)
      }
    }

  const handleRemove =
    (FieldArrayProps: any, attributeKey: number) =>
    (event: React.MouseEvent<HTMLButtonElement>) => {
      event.preventDefault()
      const { remove } = FieldArrayProps
      remove(attributeKey)
    }

  return (
    <FormikProvider value={formikProps}>
      <div className="form-control" key={variable.name}>
        <FieldArray name={variable.name}>
          {(FieldArrayProps: any) => {
            const { form } = FieldArrayProps
            const { values } = form
            if (
              values[variable.name] === undefined ||
              values[variable.name] === null ||
              values[variable.name] === ""
            ) {
              values[variable.name] = []
            }
            return (
              <div>
                {values[variable.name].map(
                  (mapData: IObjKeyPair, index: number) => (
                    <div
                      key={`${variable.name}` + index}
                      className="badge badge-info my-1 mr-1 flex h-auto w-full gap-2 px-2 py-1 md:px-4"
                    >
                      <div className="w-full">
                        {Object.keys(mapData).map(
                          (mapDataItemKey, indexInner) => (
                            <div
                              key={`${variable.name}` + indexInner}
                              className="w-full"
                              style={{ overflowWrap: "anywhere" }}
                            >
                              <span className="mr-2 font-semibold capitalize">
                                {mapDataItemKey}
                              </span>
                              {
                                //@ts-ignore
                                mapData[mapDataItemKey]
                              }
                            </div>
                          ),
                        )}
                      </div>
                      <button
                        type="button"
                        onClick={handleRemove(FieldArrayProps, index)}
                      >
                        <XMarkIcon className="h-4 w-4 cursor-pointer" />
                      </button>
                    </div>
                  ),
                )}
                <div className="mt-2 flex items-end gap-2">
                  <div className="w-full">
                    <Field
                      name="map_set_key"
                      placeholder="Name"
                      className="input input-bordered input-sm w-full"
                      onChange={inputHandler}
                    />
                    <Field
                      name="map_set_value"
                      placeholder="Description"
                      component="textarea"
                      className="textarea textarea-bordered mt-2 h-12 w-full"
                      onChange={inputHandler}
                    />
                  </div>
                  <button
                    type="button"
                    className="btn btn-primary btn-outline btn-sm mb-2"
                    onClick={onSetKeyValue(FieldArrayProps)}
                  >
                    <PlusIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
            )
          }}
        </FieldArray>
        <div className="text-faint mt-1 text-sm">{variable.description}</div>
      </div>
    </FormikProvider>
  )
}

export default PersonaListField
