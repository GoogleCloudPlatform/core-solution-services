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

// import { AppConfig } from "@/utils/AppConfig"
import { User } from "firebase/auth"
import { useTranslation } from "react-i18next"

interface UserProfileProps {
  user: User
}

const UserProfile: React.FC<UserProfileProps> = ({ user }) => {
  const { t } = useTranslation()
  return (
    <div className="card bg-base-100 overflow-visible shadow-md transition">
      <div className="card-body w-full p-4">
        <div className="flex">
          <div className="w-full">
            <div className="avatar">
              <div className="rounded-full">
                {user.photoURL ? (
                  <img
                    alt="user profile"
                    //@ts-ignore
                    src={user.photoURL}
                    className="h-5 w-5"
                    data-testid="avatar"
                  />
                ) : (
                  <div
                    className="avatar placeholder"
                    data-testid="alternate_avatar"
                  >
                    <div className="bg-base-300 w-24 rounded-full">
                      <span className="text-base-content text-4xl">
                        {user.displayName?.slice(0, 1)}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
        <div className="overflow-x-auto pl-10">
          <table className="table w-full">
            <tbody>
              <tr>
                <td className="text-dim font-semibold" data-testid="user-name">
                  {t("user-name")}
                </td>
                <td data-testid="dispalyName">{user.displayName}</td>
              </tr>
              <tr>
                <td className="text-dim font-semibold" data-testid="user-email">
                  {t("user-email")}
                </td>
                <td data-testid="email">{user.email}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default UserProfile
