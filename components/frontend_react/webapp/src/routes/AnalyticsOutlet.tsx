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

import { Outlet } from "react-router-dom"
import { useAuth } from "@/contexts/auth"
import { logEvent } from "@/utils/firebase"
import { useEffect } from "react"
import { useLocation } from "react-router-dom"

const AnalyticsOutlet = () => {
  const location = useLocation()
  const user = useAuth()

  useEffect(() => {
    logEvent("screen_view", { firebase_screen: location.pathname, user })
  }, [location.pathname])

  return <Outlet />
}

export default AnalyticsOutlet
