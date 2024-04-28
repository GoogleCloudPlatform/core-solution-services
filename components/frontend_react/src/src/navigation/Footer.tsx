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

import { AppConfig } from "@/utils/AppConfig"
import { useTranslation } from "react-i18next"

interface IFooterProps {
  showLogo?: boolean
}

const Footer: React.FC<IFooterProps> = ({ showLogo }) => {
  const { t } = useTranslation()

  return (
    <footer className="p-2">
      <div className="flex cursor-pointer gap-4 rounded-lg px-4 py-2">
        {showLogo && (
          <img src={AppConfig.simpleLogoPath} className="h-12 w-12" />
        )}
        <p className="text-faint text-primary-content mt-2 text-center text-xs">
          Google &copy; {new Date().getFullYear()}. {t("app.copyright")}
        </p>
      </div>
    </footer>
  )
}

export default Footer
