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

import Sidebar from "@/navigation/Sidebar"
import ThemeChanger from "@/navigation/ThemeChanger"
import UserDropdown from "@/navigation/UserDropdown"
import { AppConfig } from "@/utils/AppConfig"
import { classNames } from "@/utils/dom"
import { INavigationItem } from "@/utils/types"
import { Disclosure } from "@headlessui/react"
import { User } from "firebase/auth"
import { useEffect, useState } from "react"
import { useLocation } from "react-router-dom"

const Navbar = ({
  user,
  userRoutes,
}: {
  user: User
  userRoutes: INavigationItem[]
}) => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const handleClick = () => {
    setIsMenuOpen((prev) => !prev)
  }

  useEffect(() => {
    setIsMenuOpen(false)
  }, [location.pathname])

  return (
    <>
      <Disclosure as="nav" className="rounded-top-2xl bg-base-100 relative">
        {() => (
          <>
            <div className="flex h-10 items-center justify-between gap-x-2 xl:gap-x-4">
              <div
                className="hover:bg-base-300 flex cursor-pointer items-center rounded-lg p-2 transition md:hidden"
                onClick={handleClick}
              >
                <div className="i-heroicons-bars-3 block h-8 w-8" />
              </div>
              <div className="text-dim border-base-300 hidden items-center gap-2 rounded-md border px-3 py-2 tracking-tight lg:flex">
                <img
                  className="h-6"
                  src={`${AppConfig.imagesPath}/cloudlab.png`}
                  alt="GPS"
                />
                <span className="font-bold">
                  {AppConfig.siteName.split(/\s+/)[0]}
                </span>
                <span className="opacity-80">
                  {AppConfig.siteName.split(/\s+/).slice(1).join(" ")}
                </span>
              </div>
              <div className="flex items-center gap-x-2 xl:gap-x-4">
                <ThemeChanger />
                <UserDropdown user={user} userRoutes={userRoutes} />
              </div>
            </div>
            <div
              className={classNames(
                "bg-primary fixed pt-10 h-full left-0 top-0 z-50 rounded-r-xl",
                isMenuOpen ? "block" : "hidden",
              )}
            >
              <div className="hide-scrollbar overflow-y-auto md:hidden">
                <Sidebar handleClick={handleClick} />
              </div>
            </div>
          </>
        )}
      </Disclosure>
    </>
  )
}

export default Navbar
