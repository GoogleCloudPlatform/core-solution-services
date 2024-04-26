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

import { classNames } from "@/utils/dom"
import { INavigationItem } from "@/utils/types"
import React from "react"
import { useTranslation } from "react-i18next"
import { Link, matchPath, useLocation } from "react-router-dom"

type RouteListProps = {
  links: INavigationItem[]
}

const RouteList: React.FC<RouteListProps> = ({ links }) => {
  const { t } = useTranslation()
  const location = useLocation()
  const isActive = (route: string) => !!matchPath(route, location.pathname)

  return (
    <div className="flex flex-col pl-3">
      {links.map((link) => (
        <Link to={link.href} key={link.href}>
          <div
            className={classNames(
              link.show() ? "flex" : "hidden",
              isActive(link.href)
                ? "font-bold font-semibold"
                : "hover:font-bold hover:font-semibold hover:opacity-100",
              "text-md text-primary-content relative items-center gap-x-2 py-3 pl-2 tracking-wide transition",
            )}
          >
            <div
              className={classNames(
                isActive(link.href) ? "" : "hidden",
                "bg-base-100 z-100 absolute -ml-7 h-full max-h-10 w-4 rounded-r-lg",
              )}
            ></div>
            <div>{link.icon}</div>
            <div>{t(link.name)}</div>
          </div>
        </Link>
      ))}
    </div>
  )
}

export default RouteList
