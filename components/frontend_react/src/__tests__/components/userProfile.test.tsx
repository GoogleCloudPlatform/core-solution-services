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

import UserProfile from "@/components/UserProfile"
import { render, screen } from "@testing-library/react"
import { useTranslation } from "react-i18next"
import mockUser from "../../__mocks__/user"

describe("user profile", () => {
  const { t } = useTranslation()

  beforeEach(() => {
    render(<UserProfile user={mockUser} />)
  })

  it("should render avatar based on condition", async () => {
    const avatarElement = screen.queryByTestId("avatar")
    const alternateAvatarElement = screen.queryByTestId("alternate_avatar")

    mockUser.photoURL
      ? expect(avatarElement).not.toEqual(null)
      : expect(alternateAvatarElement).not.toEqual(null)
  })

  it("should render user information in table form", async () => {
    const tableElement = screen.getAllByRole("table")
    const tableRowElement = screen.getAllByRole("row")
    const tableDataElement = screen.getAllByRole("cell")
    const userName = screen.getByText(t("user-name"))
    const userEmail = screen.getByText(t("user-email"))
    const displayName = screen.queryByTestId("displayName")
    const email = screen.queryByTestId("email")

    expect(tableElement.length).toEqual(1)
    expect(tableRowElement.length).toEqual(2)
    expect(tableDataElement.length).toEqual(4)
    expect(userName).not.toEqual(null)
    expect(userName.innerHTML).toEqual(t("user-name"))
    expect(userEmail).not.toEqual(null)
    expect(userEmail.innerHTML).toEqual(t("user-email"))
    expect(displayName?.innerHTML).not.toEqual(null)
    expect(email?.innerHTML).not.toEqual(null)
  })
})
