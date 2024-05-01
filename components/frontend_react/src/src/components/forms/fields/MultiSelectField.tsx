import {
  FieldArray,
  FieldArrayRenderProps,
  FormikContextType,
  FormikProvider,
} from "formik"

import { IFormVariable } from "@/utils/types"

import FieldErrorMessage from "@/components/forms/FieldErrorMessage"

interface MultiSelectFieldProps {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const MultiSelectField: React.FC<MultiSelectFieldProps> = ({
  variable,
  formikProps,
}) => {
  const { values } = formikProps

  const isChecked = (value: unknown) => values[variable.name].includes(value)

  const onSelectValues =
    (fieldArrayProps: FieldArrayRenderProps) =>
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const selectedId = event.target.getAttribute("data-id")
      const selectedType = event.target.checked
      const { push, remove } = fieldArrayProps
      if (selectedId && selectedType) {
        push(selectedId)
      } else {
        const findIndex = values[variable.name].indexOf(selectedId)
        remove(findIndex)
      }
    }

  return (
    <FormikProvider value={formikProps}>
      <div className="form-control" key={variable.name}>
        <FieldArray name={variable.name}>
          {(fieldArrayProps: FieldArrayRenderProps) => {
            const { form } = fieldArrayProps
            const { values } = form
            if (
              values[variable.name] === undefined ||
              values[variable.name] === null ||
              values[variable.name] === ""
            ) {
              values[variable.name] = []
            }
            const unique = [...new Set(values[variable.name])]
            values[variable.name] = unique

            return (
              <div className="mt-1 w-full">
                <div className="dropdown w-full">
                  <input
                    tabIndex={0}
                    type="text"
                    placeholder="Select"
                    className="input input-bordered input-sm w-full readonly"
                    value={`Selected (${values[variable.name].length})`}
                    readOnly
                  />
                  <ul
                    tabIndex={0}
                    className="dropdown-content dropdown-open p-2 shadow bg-base-100 max-h-64 overflow-auto w-full z-50"
                  >
                    {variable.options?.map((option: any) => {
                      return (
                        <li key={option}>
                          <label className="flex items-center gap-2 p-2 cursor-pointer text-dim hover:text-normal transition hover:bg-base-200 rounded-lg">
                            <input
                              type="checkbox"
                              className="checkbox checkbox-sm"
                              data-id={option}
                              onChange={onSelectValues(fieldArrayProps)}
                              checked={isChecked(option)}
                            />
                            <span className="font-semibold">{option}</span>
                          </label>
                        </li>
                      )
                    })}
                  </ul>
                </div>
              </div>
            )
          }}
        </FieldArray>
        <FieldErrorMessage variableName={variable.name} />
        <div className="text-sm text-faint mt-1">{variable.description}</div>
      </div>
    </FormikProvider>
  )
}

export default MultiSelectField
