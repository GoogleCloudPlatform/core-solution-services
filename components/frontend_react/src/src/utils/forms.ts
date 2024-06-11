// Copyright 2024 Google LLC
//
// Licensed under the Apache License, Version 2.0 (the License);
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import axios from "axios"
import groupBy from "lodash/groupBy"
import fileDownload from "js-file-download"
import { IFormVariable, IFormValidationData } from "@/utils/types"
import * as yup from "yup"
import startCase from "lodash/startCase"

export const groupVariables = (variableList: IFormVariable[]) =>
  groupBy(variableList, "group")

export const initialFormikValues = (variableList: IFormVariable[]) => {
  let initialFormData = variableList.reduce((formatDefault, formVarsdata) => {
    const defaultValue = formVarsdata.default !== "" ? formVarsdata.default : ""
    return { ...formatDefault, [formVarsdata.name]: defaultValue }
  }, {})

  return initialFormData
}

export const fileNameByPath = (filePath: string) => {
  if (filePath) {
    const fileNameArr = filePath.split("/")
    const fileName = fileNameArr[fileNameArr.length - 1]
    return fileName
  } else {
    return null
  }
}

export const getFileURL = async (pathURL: string, userToken: string) => {
  const downloadURL = `${process.env.NEXT_PUBLIC_API_BASE_URL}/demos/downloadFile/?filePath=${pathURL}`
  try {
    const res = await axios.get(downloadURL, {
      headers: {
        Authorization: `Bearer ${userToken}`,
      },
    })
    return res.data.url as string
  } catch (error) {
    console.error(error)
    return null
  }
}


export const downloadFile = async (
  filePath: string,
  fileName: string,
  userToken: string,
) => {
  const downloadURL = (await getFileURL(filePath, userToken)) as string | null

  if (!downloadURL) {
    throw new Error(`File not found: ${fileName}`)
  }

  if (window) {
    window.open(downloadURL)
    return
  }

  return axios
    .get(downloadURL, {
      responseType: "blob",
      // headers: {
      //   Authorization: `Bearer ${userToken}`,
      // },
    })
    .then((res) => {
      fileDownload(res.data, fileName)
    })
}

export const formValidationSchema = (variableList: IFormVariable[]) => {
  let formValidationData: IFormValidationData = {}

  variableList.forEach((variable) => {
    variable.required
      ? (formValidationData[variable.name] = yup
          .string()
          .min(4, "Too Short!")
          .max(20, "Too Long!")
          .required(`A value for ${startCase(variable.name)} is required`))
      : {}
  })

  const formValidationResult = yup.object().shape(formValidationData)

  return formValidationResult
}
