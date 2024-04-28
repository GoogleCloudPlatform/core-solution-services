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

import { ReactNode, useEffect, useState } from "react"
import { getAnalytics } from "@/utils/firebase"
import Loading from "@/navigation/Loading"
import Authenticated from "@/templates/Authenticated"
import Unauthenticated from "@/templates/Unauthenticated"
import { useAuth } from "@/contexts/auth"

type IMainProps = {
  meta: ReactNode
  children: ReactNode
}

const Main = (props: IMainProps) => {
  const { user, loading } = useAuth()
  const [loadedGA, setLoadedGA] = useState(false)

  useEffect(() => {
    if (!loadedGA) {
      getAnalytics()
      setLoadedGA(true)
    }
  }, [])

  if (loading) return <Loading />

  // @ts-ignore TODO: Fix error
  if (!user || !token) return <Unauthenticated {...props} />

  return <Authenticated user={user} {...props} />
}
export { Main }
