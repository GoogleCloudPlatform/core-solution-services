import { useState, useEffect } from "react"
import { Form, useFormik, FormikProvider } from "formik"
import {
  DemoPriorities,
  CloudProducts,
  UseCases,
  SalesTags,
  AccreditationStatus,
} from "@gps-demos/demo-portal-types"
import { GenericDemo, IDemo } from "@gps-demos/demo-portal-types/src/types"
import DemoFormFields from "@/components/forms/DemoFormFields"
import Link from "next/link"
import { IFormValidationData, IFormVariable } from "@/utils/types"
import { formValidationSchema, initialFormikValues } from "@/utils/forms"

interface NewDemoFormProps {
  demo: GenericDemo | null
  onSubmit: Function
  onSuccess: Function
  onFailure: Function
  token: string
  currentVarsData: IFormVariable[]
}

const NewDemoForm: React.FunctionComponent<NewDemoFormProps> = ({
  onSubmit,
  onSuccess,
  onFailure,
  demo,
  token,
  currentVarsData,
}) => {
  const [submitting, setSubmitting] = useState(false)
  const [demoInitialFormat, setDemoInitialFormat] = useState({})

  const defaultValues = initialFormikValues(currentVarsData)

  const handleFiles = (_files: FileList, _uploadVariable: string) => {
    //handle file upload if required in future
  }

  const handleSubmit = async (values: Record<string, any>) => {
    const priority =
      values.priority ?? DemoPriorities[DemoPriorities.length - 1] // Default to lowest priority

    values = {
      ...values,
      // @ts-ignore
      priority: parseInt(priority),
    }

    const {
      cloudProducts,
      useCases,
      salesTags,
      accreditationStatus,
      filesfileHideInPDP,
      ...restValues
    } = values

    const tags = cloudProducts
      .concat(useCases)
      .concat(salesTags)
      .concat(accreditationStatus)

    const payloadData: IDemo | Record<string, any> = Object.assign(
      {},
      restValues,
      { tags: tags },
    )

    try {
      setSubmitting(true)
      const result = await onSubmit(payloadData)
      await onSuccess(result)
    } catch (error) {
      await onFailure(error)
    } finally {
      setSubmitting(false)
    }
  }

  useEffect(() => {
    if (demo && demo !== null) {
      const { tags, ...restDemoValues } = demo
      if (
        //@ts-ignore
        restDemoValues?.partnerId === null ||
        //@ts-ignore
        restDemoValues?.partnerId === undefined
      ) {
        //@ts-ignore
        delete restDemoValues?.partnerId
      }

      const cloudProducts = [...CloudProducts].filter((cp) =>
        tags?.includes(cp),
      )
      const useCases = [...UseCases].filter((uc) => tags?.includes(uc))
      const salesTags = [...SalesTags].filter((st) => tags?.includes(st))
      const accreditationStatus = [...AccreditationStatus].filter((as) =>
        tags?.includes(as),
      )

      const demoInitialFormating = Object.assign(
        {},
        restDemoValues,
        { cloudProducts: cloudProducts },
        { useCases: useCases },
        { salesTags: salesTags },
        { accreditationStatus: accreditationStatus },
      )
      setDemoInitialFormat(demoInitialFormating)
    }
  }, [demo])

  const initialValues = Object.assign({}, defaultValues, demoInitialFormat)

  const formValidationData: IFormValidationData =
    formValidationSchema(currentVarsData)

  const formik = useFormik({
    initialValues: initialValues,
    enableReinitialize: true,
    validateOnMount: true,
    validationSchema: formValidationData,
    onSubmit: async (values) => {
      await handleSubmit(values)
    },
  })

  return (
    <div className="w-full">
      <FormikProvider value={formik}>
        <Form spellCheck="true">
          {currentVarsData ? (
            <DemoFormFields
              variableList={currentVarsData}
              formikProps={formik}
              demo={demo}
              token={token}
              handleFiles={handleFiles}
            />
          ) : (
            <></>
          )}

          <div className="mt-2 flex justify-between">
            <Link href="#">
              <button
                className="btn btn-outline btn-sm"
                onClick={() => window.history.go(-1)}
              >
                Back
              </button>
            </Link>
            <button
              className="btn btn-primary btn-sm"
              type="submit"
              disabled={Boolean(
                submitting || Object.keys(formik.errors).length,
              )}
            >
              {demo?.id ? "Update" : "Submit"}
            </button>
          </div>
        </Form>
      </FormikProvider>
    </div>
  )
}

export default NewDemoForm
