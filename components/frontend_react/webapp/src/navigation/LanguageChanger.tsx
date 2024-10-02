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

import { useTranslation } from "react-i18next"
import { supportedLangs } from "@/utils/lang"

const LanguageChanger = () => {
  const { i18n } = useTranslation()

  const changeLanguage = (code: string) => {
    console.log("Change Language:", code)
    i18n.changeLanguage(code)
  }

  return (
    <select
      name="lang"
      id="lang"
      className="select-bordered select"
      onChange={(e) => changeLanguage(e.target.value)}
      value={i18n?.language || "en"}
    >
      {supportedLangs.map((lang) => (
        <option value={lang.code} key={lang.code}>
          {lang.flag}&nbsp;&nbsp;{lang.name}
        </option>
      ))}
    </select>
  )
}

export default LanguageChanger
