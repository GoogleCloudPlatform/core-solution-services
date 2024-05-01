import { Field, FieldArray, FormikContextType, FormikProvider } from "formik"
import { PlusIcon, XMarkIcon } from "@heroicons/react/24/outline"
import { useState } from "react"

import { IFormVariable } from "@/utils/types"

interface ListField {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const ListField: React.FC<ListField> = ({ variable, formikProps }) => {
  const [formFieldValue, setFormFieldValue] = useState("")

  const inputHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    setFormFieldValue(event.target.value)
  }

  const onSetValue =
    (FieldArrayPropsPush: Function) =>
    (event: React.MouseEvent<HTMLButtonElement>) => {
      event.preventDefault()
      if (formFieldValue) {
        FieldArrayPropsPush(formFieldValue)
      }
      setFormFieldValue("")
    }

  const handleKeyboardEvent =
    (FieldArrayPropsPush: Function) =>
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === "Enter") {
        e.preventDefault()
        if (formFieldValue) {
          FieldArrayPropsPush(formFieldValue)
        }
        setFormFieldValue("")
      }
    }

  return (
    <FormikProvider value={formikProps}>
      <div className="form-control" key={variable.name}>
        <FieldArray name={variable.name}>
          {(FieldArrayProps: any) => {
            const { push, remove, form } = FieldArrayProps
            const { values } = form
            //@ts-ignore
            const unique = [...new Set(values[variable.name])]
            values[variable.name] = unique
            return (
              <div>
                {values[variable.name].map(
                  (setvalue: string, index: number) => (
                    <div
                      key={index}
                      className="badge badge-info gap-2 my-1 mr-1 w-auto h-auto py-1 px-2 md:px-4"
                    >
                      <span
                        className="w-auto"
                        style={{ overflowWrap: "anywhere" }}
                      >
                        {setvalue}
                      </span>
                      <XMarkIcon
                        onClick={() => remove(index)}
                        className="h-6 w-6 cursor-pointer"
                      />
                    </div>
                  ),
                )}
                <div className="mt-1 flex">
                  <Field
                    name="listfield"
                    className="input input-bordered input-sm w-full"
                    value={formFieldValue}
                    onChange={inputHandler}
                    onKeyDown={handleKeyboardEvent(push)}
                  />
                  <button
                    type="button"
                    className="btn btn-primary btn-outline btn-sm ml-2"
                    onClick={onSetValue(push)}
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

export default ListField
