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
import SignInForm from "@/navigation/SignInForm"
import { AppConfig } from "@/utils/AppConfig"

const Signin = () => {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen px-4 md:px-10">
      <div className="flex min-h-screen max-w-6xl items-center justify-center">
        <div className="mx-auto w-3/4 text-center md:w-1/2">
          <div className="flex items-center justify-center">
            <img
              className="h-20 w-auto pr-6"
              src={AppConfig.logoPath}
              alt={t("app.title")}
            />
            <div className="text-center text-xl font-semibold">
              {t("app.title")}
            </div>
          </div>

          <div className="mb-16 mt-4">{t("app.description")}</div>

          <div className="sm:px-20 md:px-10 lg:px-0 xl:px-20">
            <SignInForm authOptions={AppConfig.authProviders} />
          </div>
        </div>
      </div>
    </div>
  )
}

export default Signin
