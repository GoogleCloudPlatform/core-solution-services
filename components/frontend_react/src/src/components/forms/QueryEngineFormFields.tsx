import sortBy from "lodash/sortBy"

import { GenericDemo } from "@gps-demos/demo-portal-types/src/types"
import { groupByOrderVariables } from "@/utils/forms"
import { classNames } from "@/utils/dom"

import FileNestedField from "@/components/forms/fields/FileNestedField"
import ListField from "@/components/forms/fields/ListField"
import SelectField from "@/components/forms/fields/SelectField"
import { IFormVariable } from "@/utils/types"
import BooleanField from "@/components/forms/fields/BooleanField"
import StringField from "@/components/forms/fields/StringField"
import TextareaField from "@/components/forms/fields/TextareaField"
import TeamListField from "@/components/forms/fields/TeamListField"
import PersonaListField from "@/components/forms/fields/PersonaListField"
import FileUploadField from "@/components/forms/fields/FileUploadField"
import DateField from "@/components/forms//fields/DateField"
import OtherFileNestedField from "@/components/forms/fields/OtherFileNestedField"
import MultiSelectField from "@/components/forms/fields/MultiSelectField"

interface DemoFormFieldsProps {
  variableList: IFormVariable[]
  formikProps: any
  demo: GenericDemo | null
  token: string
  handleFiles: Function
}

const DemoFormFields: React.FC<DemoFormFieldsProps> = ({
  variableList,
  formikProps,
  demo,
  token,
  handleFiles,
}) => {
  const sortedList = sortBy(variableList, "order")
  const groupSortedList: any = groupByOrderVariables(sortedList)

  const renderControls = (variable: IFormVariable) => {
    switch (variable.type) {
      case "string":
        return <StringField variable={variable} formikProps={formikProps} />

      case "string(textarea)":
        return <TextareaField variable={variable} formikProps={formikProps} />

      case "bool":
        return <BooleanField variable={variable} formikProps={formikProps} />

      case "select":
        return <SelectField variable={variable} formikProps={formikProps} />

      case "multiselect":
        return (
          <MultiSelectField variable={variable} formikProps={formikProps} />
        )

      case "date":
        return <DateField variable={variable} formikProps={formikProps} />

      case "file":
        return <FileNestedField variable={variable} formikProps={formikProps} />

      case "file(upload)":
        return (
          <FileUploadField
            variable={variable}
            formikProps={formikProps}
            demo={demo}
            token={token}
            handleFilesUpload={handleFiles}
          />
        )

      case "file(other)":
        return (
          <OtherFileNestedField variable={variable} formikProps={formikProps} />
        )

      case "list(string)":
        return <ListField variable={variable} formikProps={formikProps} />

      case "team(list)":
        return <TeamListField variable={variable} formikProps={formikProps} />

      case "persona(list)":
        return (
          <PersonaListField variable={variable} formikProps={formikProps} />
        )

      default:
        return <StringField variable={variable} formikProps={formikProps} />
    }
  }

  return (
    <div className="flex-wrap">
      {Object.keys(groupSortedList).map((groupSortedListKey) => (
        <div
          className="w-full"
          key={groupSortedList[groupSortedListKey][0].name}
        >
          <div className="w-full gap-4 md:flex">
            {groupSortedList[groupSortedListKey].map(
              (variable: IFormVariable) => (
                <div
                  className={classNames(
                    formikProps.values.hasOwnProperty("partnerId") &&
                      variable.name === "visibleToPartners"
                      ? "hidden"
                      : "",
                    "relative w-full",
                  )}
                  key={variable.name}
                >
                  <label
                    htmlFor={variable.name}
                    className="mb-1 flex text-xs font-semibold"
                  >
                    {variable.display}
                    {variable.required && (
                      <div className="ml-1 text-error">*</div>
                    )}
                  </label>
                  {formikProps.values.hasOwnProperty("partnerId") &&
                  variable.name === "visibleToPartners"
                    ? ""
                    : renderControls(variable)}
                </div>
              ),
            )}
          </div>
        </div>
      ))}
    </div>
  )
}

export default DemoFormFields
