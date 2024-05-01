import { ErrorMessage } from "formik"

interface IFieldErrorMessageProps {
  variableName: string
}

const FieldErrorMessage: React.FC<IFieldErrorMessageProps> = ({
  variableName,
}) => {
  return (
    <div className="mt-1 text-xs text-error">
      <ErrorMessage name={variableName} />
    </div>
  )
}

export default FieldErrorMessage
