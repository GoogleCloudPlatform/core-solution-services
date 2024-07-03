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

// https://github.com/pmndrs/zusta
import create from "zustand"
import { User as FirebaseUser } from "firebase/auth"

interface IUserState {
  user: null | FirebaseUser
  setUser: (user: null | FirebaseUser) => void
  isAdmin: boolean
  setIsAdmin: (isAdmin: boolean) => void
  authToken: null | string
  setAuthToken: (authToken: null | string) => void
  isPartnerManager: boolean
  setIsPartnerManager: (isPartnerManager: boolean) => void
}

const useStore = create<IUserState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
  isAdmin: false,
  setIsAdmin: (isAdmin) => set({ isAdmin }),
  authToken: null,
  setAuthToken: (authToken) => set({ authToken }),
}))

export default useStore
