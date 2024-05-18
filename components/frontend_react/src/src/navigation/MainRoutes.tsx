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

import RouteList from "@/navigation/RouteList"
import { INavigationItem } from "@/utils/types"
import { PlusIcon } from "@heroicons/react/24/outline"
import { classNames } from "@/utils/dom"
import themeStore from "@/store/theme"

const theme = themeStore((state) => state.theme)

// These are i18n link names, put the label in the common.json file
export const links: INavigationItem[] = [
  {
    name: "Chat History",
    href: "/conversations",
    show: () => true,
    icon: <div className="i-heroicons-tag h-5 w-5" />,
  },
  {
    name: "Home",
    href: "/",
    show: () => false,
    icon: <div className="i-heroicons-home h-5 w-5" />,
  },
  {
    name: "New Chat",
    href: "/aichat",
    show: () => true,
    icon: (
      <div className="i-heroicons-sparkles-solid text-primary-content h-6 w-6" />
    ),
  },
  {
    name: "Query Engines",
    href: "/queryengines",
    show: () => true,
    icon: <div className="i-heroicons-tag h-5 w-5" />,
  },
  {
    name: "Add Query Engine",
    href: "/queryengines/new",
    show: () => true,
    icon: (
      <PlusIcon
        className={classNames(
          theme === "light" ? "text-primary-content" : "text-base-content",
          "h-5 w-5",
        )}
      />
    ),
  },
  {
    name: "Query History",
    href: "/queries",
    show: () => true,
    icon: <div className="i-heroicons-tag h-5 w-5" />,
  },
  {
    name: "New Query",
    href: "/aiquery",
    show: () => true,
    icon: (
      <div className="i-heroicons-sparkles-solid text-primary-content h-6 w-6" />
    ),
  },
]

export const MainRoutes = () => {
  return <RouteList links={links} />
}
