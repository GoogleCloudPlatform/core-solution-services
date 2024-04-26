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

import { INavigationItem, IAppConfig } from "@/utils/types"

// Make sure you update your public/locales JSON files
export const AppConfig: IAppConfig = {
  siteName: "GenAI for Public Sector",
  locale: "en",
  logoPath: "/assets/images/rit-logo.png",
  simpleLogoPath: "/assets/images/rit-brain.png",
  imagesPath: "/assets/images",
  theme: "light",
  authProviders: ["google", "password"],
  authorizedDomains: [/@google\.com$/i, /@\w+\.altostrat\.com$/i],
}

// // These are i18n link names, put the label in the common.json file
// export const MainNavigation: INavigationItem[] = [
//   { name: "link.about", href: "/about", show: () => true },
//   { name: "link.users", href: "/users", show: () => true },
//   { name: "link.firestore", href: "/firestore", show: () => true },
//   { name: "link.icons", href: "/icons", show: () => true },
//   { name: "link.table", href: "/table", show: () => true },
// ]

export const UserNavigation: INavigationItem[] = [
  { name: "link.profile", href: "/profile", show: () => true },
  { name: "link.settings", href: "/settings", show: () => false },
  { name: "link.signout", href: "/signout", show: () => true },
]

export const FooterNavigation: INavigationItem[] = [
  { name: "link.about", href: "/about", show: () => true },
]

// Full list of scopes: https://developers.google.com/identity/protocols/oauth2/scopes
export const OAuthScopes: string[] = []
