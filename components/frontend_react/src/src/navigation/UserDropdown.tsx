/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import { classNames } from "@/utils/dom"
import { INavigationItem } from "@/utils/types"
import { Menu, Transition } from "@headlessui/react"
import { User } from "firebase/auth"
import { Link } from "react-router-dom"
import { Fragment } from "react"
import { useTranslation } from "react-i18next"

type IUserDropdownProps = {
  user: User
  userRoutes: INavigationItem[]
}

const UserDropdown: React.FC<IUserDropdownProps> = ({ user, userRoutes }) => {
  const { t } = useTranslation()

  return (
    <Menu as="div" className="relative flex-shrink-0">
      <Menu.Button
        data-testid="user-menu-button"
        className="bg-base-100 focus:ring-primary border-base-300 flex max-w-xs items-center gap-2 rounded-xl border px-3 text-sm focus:outline-none focus:ring-2 focus:ring-offset-2"
      >
        <div className="i-logos-google w-12 text-5xl" />
        <span className="sr-only">Open user menu</span>
        {user?.photoURL ? (
          <img
            data-testid="user-img"
            className="h-8 w-8 rounded-full"
            src={user.photoURL}
            alt={user.displayName || ""}
          />
        ) : (
          <></>
        )}
      </Menu.Button>
      <Transition
        as={Fragment}
        enter="transition ease-out duration-200"
        enterFrom="transform opacity-0 scale-90"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-90"
      >
        <Menu.Items className="ring-base-300 bg-base-100 absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md py-1 shadow-lg ring-1 focus:outline-none">
          {userRoutes.map(
            (item) =>
              item.show() && (
                <Menu.Item key={item.name}>
                  {({ active }) => (
                    <a
                      key={item.name}
                      href={item.href}
                      className={classNames(
                        active
                          ? "text-primary bg-base-200 "
                          : "text-base-content hover:bg-base-200",
                        "block px-4 py-2 text-sm font-semibold",
                      )}
                    >
                      {t(item.name)}
                    </a>
                  )}
                </Menu.Item>
              ),
          )}
        </Menu.Items>
      </Transition>
    </Menu>
  )
}

export default UserDropdown
