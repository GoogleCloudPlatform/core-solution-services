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

import Navbar from "@/navigation/Navbar"
import { AuthAppRouter } from "@/routes/AppRouter"
import { UserNavigation } from "@/utils/AppConfig"
import { User } from "firebase/auth"

interface IMainContent {
  user: User
}

const MainContent: React.FC<IMainContent> = ({ user }) => {
  return (
    <div className="bg-base-100 border-primary/80 flex min-h-[calc(100vh-1.5rem)] max-h-[calc(100vh-20.3rem)] flex-col rounded-none border-2 px-4 py-4 md:rounded-2xl md:px-6 xl:px-10 xl:py-6">
      <Navbar user={user} userRoutes={UserNavigation} />
      <div className="bg-base-100 mt-8 flex flex-grow flex-col">
        <AuthAppRouter user={user} />
      </div>
    </div>
  )
}

export default MainContent
