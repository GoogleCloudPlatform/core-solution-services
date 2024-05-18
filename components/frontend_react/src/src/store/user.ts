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
