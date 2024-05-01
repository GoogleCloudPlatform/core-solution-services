import { Field, FormikContextType, FormikProvider } from "formik"

import { IFormVariable } from "@/utils/types"

import FieldErrorMessage from "@/components/forms/FieldErrorMessage"

interface ITextareaFieldProps {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const TextareaField: React.FC<ITextareaFieldProps> = ({
  variable,
  formikProps,
}) => {
  return (
    <FormikProvider value={formikProps}>
      <div className="form-control" key={variable.name}>
        <Field
          id={variable.name}
          name={variable.name}
          placeholder={variable.display}
          component="textarea"
          className="textarea textarea-bordered h-12 w-full"
        />
        <FieldErrorMessage variableName={variable.name} />
        <div className="text-faint mt-1 text-sm">{variable.description}</div>
      </div>
    </FormikProvider>
  )
}

export default TextareaField
