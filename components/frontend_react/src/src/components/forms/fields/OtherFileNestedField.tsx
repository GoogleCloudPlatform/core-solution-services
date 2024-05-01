import { Field, FieldArray, FormikContextType, FormikProvider } from "formik"
import { PlusIcon, XMarkIcon } from "@heroicons/react/24/outline"
import { useState } from "react"
import { useRouter } from "next/router"

import { IFormVariable } from "@/utils/types"
import {
  FileType,
  DemoStage,
  SalesPlayStage,
} from "@gps-demos/demo-portal-types"
import {
  IFileType,
  IDemoFiles,
  ISalesPlayFiles,
} from "@gps-demos/demo-portal-types/src/types"
import FileListDisplay from "@/components/forms/FileListDisplay"

interface IOtherFileNestedField {
  variable: IFormVariable
  formikProps: FormikContextType<any>
}

const OtherFileNestedField: React.FC<IOtherFileNestedField> = ({
  variable,
  formikProps,
}) => {
  const router = useRouter()

  const checkSalesPlayPage = router.pathname.includes("sales-plays")
  const dataSalesPlayStage = Object.values(SalesPlayStage.Values)
  const dataDemoStage = Object.values(DemoStage.Values)

  const fileFormatDefault = {
    type: variable.fileType,
    name: "",
    href: "",
    stage: checkSalesPlayPage ? dataSalesPlayStage[0] : dataDemoStage[0] || "",
    description: "",
    hideInPDP: false,
  }
  const [fileFormat] = useState(fileFormatDefault)
  const { errors } = formikProps

  const inputHandler = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.name === `${variable.name}fileLink`) {
      fileFormat.href = event.target.value
    }
    if (event.target.name === `${variable.name}fileName`) {
      fileFormat.name = event.target.value
    }
    if (event.target.name === `${variable.name}fileDescription`) {
      fileFormat.description = event.target.value
    }
  }

  const selectHandler = (event: React.ChangeEvent<HTMLSelectElement>) => {
    if (event.target.name === `${variable.name}fileType`) {
      fileFormat.type = event.target.value
    }
  }

  const selectStageHandler = (event: React.ChangeEvent<HTMLSelectElement>) => {
    if (
      event.target.name === `${variable.name}fileStage` &&
      event.target.value !== undefined
    ) {
      fileFormat.stage = event.target.value
    }
  }

  const onSetKeyValue =
    (FieldArrayProps: any) => (event: React.MouseEvent<HTMLButtonElement>) => {
      event.preventDefault()
      const { push, form } = FieldArrayProps
      const { values } = form

      if (fileFormat.href) {
        fileFormat.hideInPDP = values["filesfileHideInPDP"]
        push(fileFormat)
      }
    }

  const handleRemove =
    (FieldArrayProps: any, attributeKey: number) =>
    (event: React.MouseEvent<HTMLButtonElement>) => {
      event.preventDefault()
      const { remove } = FieldArrayProps
      remove(attributeKey)
    }

  const fileTypeDataFilterd = Object.values(FileType.Values).filter(
    (fileTypeData) => fileTypeData !== variable.fileType,
  )

  const renderSalesPlayStageList = () => {
    return dataSalesPlayStage.map((optionSalesPlayStage: ISalesPlayFiles) => {
      return (
        <option key={optionSalesPlayStage} value={optionSalesPlayStage}>
          {optionSalesPlayStage}
        </option>
      )
    })
  }

  const renderDemoStageList = () => {
    return dataDemoStage.map((optionDemoStage: IDemoFiles) => {
      return (
        <option key={optionDemoStage} value={optionDemoStage}>
          {optionDemoStage}
        </option>
      )
    })
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
                  (mapData: IDemoFiles | ISalesPlayFiles, index: number) => (
                    <div
                      key={`${variable.name}` + mapData.name}
                      className="badge badge-info my-1 mr-1 flex h-auto w-full gap-2 px-2 py-1 md:px-4"
                    >
                      <div className="w-full">
                        <FileListDisplay
                          label="File Type"
                          value={mapData.type}
                        />
                        <FileListDisplay
                          label="File Category"
                          value={mapData.stage}
                        />
                        <FileListDisplay
                          label="File Name"
                          value={mapData.name}
                        />
                        <FileListDisplay
                          label="File Link"
                          value={mapData.href}
                        />
                        <FileListDisplay
                          label="File Description"
                          value={mapData.description}
                        />
                        {!checkSalesPlayPage && (
                          <FileListDisplay
                            label=" File Hidden in PDP"
                            value={mapData.hideInPDP ? "True" : "False"}
                          />
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
                <div className="mt-2 w-full">
                  {
                    //@ts-ignore
                    errors[variable.name]
                      ? //@ts-ignore
                        errors[variable.name][errors[variable.name].length - 1]
                          ?.href && (
                          <div className="text-error text-xs mt-1">
                            {
                              //@ts-ignore
                              errors[variable.name][
                                //@ts-ignore
                                errors[variable.name].length - 1
                              ]?.href
                            }
                          </div>
                        )
                      : ""
                  }
                  <div className="mt-1 w-full justify-between sm:flex sm:gap-2">
                    <div className="w-full">
                      <Field
                        name={`${variable.name}fileLink`}
                        placeholder="File Link"
                        className="input input-bordered input-sm w-full"
                        onChange={inputHandler}
                      />
                    </div>
                    <Field
                      name={`${variable.name}fileName`}
                      placeholder="File Name"
                      className="input input-bordered input-sm w-full mt-2 sm:mt-0"
                      onChange={inputHandler}
                    />
                  </div>
                  <div className="mt-2 w-full">
                    <Field
                      name={`${variable.name}fileDescription`}
                      placeholder="File Description"
                      component="textarea"
                      className="textarea textarea-bordered h-12 w-full"
                      onChange={inputHandler}
                    />
                  </div>
                  <div className="mt-2 w-full flex">
                    <Field
                      as="select"
                      name={`${variable.name}fileType`}
                      className="select select-bordered select-sm font-normal w-full mr-2"
                      onChange={selectHandler}
                    >
                      <option value={variable.fileType ?? ""}>
                        {variable.fileType ?? "Select File Type"}
                      </option>
                      {fileTypeDataFilterd.map((option: IFileType) => {
                        return (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        )
                      })}
                    </Field>
                    <Field
                      as="select"
                      name={`${variable.name}fileStage`}
                      className="select select-bordered select-sm font-normal w-full mr-2"
                      onChange={selectStageHandler}
                    >
                      {checkSalesPlayPage
                        ? renderSalesPlayStageList()
                        : renderDemoStageList()}
                    </Field>
                    {!checkSalesPlayPage && (
                      <div className="w-full sm:w-96">
                        <label className="label cursor-pointer">
                          <span className="label-text text-xs font-semibold">
                            Hide in PDP?
                          </span>
                          <Field
                            id={`${variable.name}fileHideInPDP`}
                            name={`${variable.name}fileHideInPDP`}
                            type="checkbox"
                            className="toggle toggle-primary mr-2"
                          />
                        </label>
                      </div>
                    )}
                    <button
                      type="button"
                      className="btn btn-primary btn-outline btn-sm mb-2"
                      onClick={onSetKeyValue(FieldArrayProps)}
                    >
                      <PlusIcon className="h-4 w-4" />
                    </button>
                  </div>
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

export default OtherFileNestedField
