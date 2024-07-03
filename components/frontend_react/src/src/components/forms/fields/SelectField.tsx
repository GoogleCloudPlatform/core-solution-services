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

import React from "react"
import { Field, FormikContextType, FormikProvider } from "formik"
import { IFormVariable } from "@/utils/types"
import FieldErrorMessage from "@/components/forms/FieldErrorMessage"
import startCase from "lodash.startcase"

interface SelectField {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const SelectField: React.FC<SelectField> = ({ variable, formikProps }) => {
  return (
    <FormikProvider value={formikProps}>
      <div className="form-control" key={variable.name}>
        <Field
          as="select"
          id={variable.name}
          name={variable.name}
          className="select select-bordered select-sm font-normal"
        >
          <option value="">Select</option>
          {variable.options?.map((option: any) => {
            let selectOption: string = option
            let selectValue: string = option
            if (typeof option == 'object') {
              selectOption = option.option
              selectValue = option.value
            }
            return (
              <option key={selectOption} value={selectValue}>
                {selectOption}
              </option>
            )
          })}
        </Field>
        <FieldErrorMessage variableName={variable.name} />
        <div className="text-faint mt-1 text-sm">{variable.description}</div>
      </div>
    </FormikProvider>
  )
}

export default SelectField
