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

import { useAuth } from "@/contexts/auth"
import { AIChatRoute, AIQueryRoute } from "@/routes/AIRoute"
import About from "@/routes/About"
import AnalyticsOutlet from "@/routes/AnalyticsOutlet"
import Conversations from "@/routes/Conversations"
import Queries from "@/routes/Queries"
import QueryEngines from "@/routes/QueryEngines"
import NewQueryEngine from "@/routes/NewQueryEngine"
import Firestore from "@/routes/FirestoreUsers"
import Home from "@/routes/Home"
import NotFound from "@/routes/NotFound"
import Profile from "@/routes/Profile"
import SignOut from "@/routes/SignOut"
import Signin from "@/routes/Signin"
import { User } from "firebase/auth"
import { Route, Routes } from "react-router-dom"

interface NoAuthAppRouterProps {}

interface AuthAppRouterProps {
  user: User
}

export const AuthAppRouter: React.FunctionComponent<AuthAppRouterProps> = ({
  user,
}) => {
  const { token } = useAuth()

  return (
    <Routes>
      <Route path="/" element={<AnalyticsOutlet />}>
        <Route path="/" element={<Home />} />
        <Route
          path="/conversations"
          element={<Conversations token={token!} />}
        />
        <Route
          path="/queries"
          element={<Queries token={token!} />}
        />
        <Route
          path="/queryengines"
          element={<QueryEngines token={token!} />}
        />
        <Route
          path="/queryengines/new"
          element={<NewQueryEngine token={token!} />}
        />
        <Route path="/about" element={<About />} />
        <Route path="/aichat" element={<AIChatRoute />} />
        <Route path="/aiquery" element={<AIQueryRoute />} />
        <Route path="/profile" element={<Profile user={user} />} />
        <Route path="/signout" element={<SignOut />} />
        <Route path={"/firestore"} element={<Firestore />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  )
}

export const NoAuthAppRouter: React.FunctionComponent<
  NoAuthAppRouterProps
> = () => {
  return (
    <Routes>
      <Route path="/" element={<AnalyticsOutlet />}>
        <Route path="/signin" element={<Signin />} />
      </Route>
    </Routes>
  )
}
