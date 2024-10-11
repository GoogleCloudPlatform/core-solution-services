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

interface BooleanFieldProps {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const BooleanField: React.FC<BooleanFieldProps> = ({
  variable,
  formikProps,
}) => {
  return (
    <FormikProvider value={formikProps}>
      <div className="form-control" key={variable.name}>
        <div className="flex justify-between">
          <label className="relative inline-flex cursor-pointer items-center">
            <Field
              id={variable.name}
              type="checkbox"
              className="peer toggle toggle-sm sr-only"
              name={variable.name}
              onClick={() => { variable.onClick() }}
            />
            <div className="peer-focus:ring-7 h-6 w-11 rounded-full bg-base-300 after:absolute after:left-[2px] after:top-[2px] after:h-5 after:w-5 after:rounded-full after:border-primary after:border-primary after:bg-base-100 after:transition-all after:content-[''] peer-checked:bg-primary peer-checked:after:translate-x-full peer-checked:after:border-primary peer-focus:outline-none peer-focus:ring-primary dark:peer-focus:ring-primary"></div>
          </label>
        </div>
        <div className="text-faint mt-1 text-sm">{variable.description}</div>
      </div>
    </FormikProvider>
  )
}

export default BooleanField
