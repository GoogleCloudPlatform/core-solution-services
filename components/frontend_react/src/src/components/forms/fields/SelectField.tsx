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
            return (
              <option key={option} value={option}>
                {variable.name === "priority"
                  ? `P${option}`
                  : variable.name === "classification"
                  ? startCase(option as string)
                  : option}
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
