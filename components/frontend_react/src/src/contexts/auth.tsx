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

import { useState, useEffect, useContext, createContext } from "react"
import nookies from "nookies"
import { auth } from "@/utils/firebase"
import { useNavigate } from "react-router-dom"
import { User, onIdTokenChanged } from "firebase/auth"

const AuthContext = createContext<{
  user: User | null
  token: string | null
  loading: boolean
}>({
  user: null,
  token: null,
  loading: true,
})

export function AuthProvider({ children }: any) {
  const navigate = useNavigate()
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState<boolean>(true)

  useEffect(() => {
    return onIdTokenChanged(auth, async (user) => {
      setLoading(false)
      if (!user) {
        setUser(null)
        nookies.destroy(null, "token")
        nookies.set(null, "token", "", { path: "/" })
        navigate("/signin")
        return
      }

      const token = await user.getIdToken()
      setToken(token)
      setUser(user)
      //console.log({ user, token })
      nookies.destroy(null, "token")
      nookies.set(null, "token", token, { path: "/" })
    })
  }, [])

  // force refresh the token every 10 minutes
  useEffect(() => {
    const handle = setInterval(
      async () => {
        if (user) await user.getIdToken(true)
      },
      10 * 60 * 1000,
    )

    return () => clearInterval(handle)
  }, [user])

  return (
    <AuthContext.Provider value={{ user, loading, token }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  return useContext(AuthContext)
}
