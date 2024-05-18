import { Theme } from "@/utils/types"
import create from "zustand"

interface IThemeStore {
  theme: Theme
  setTheme: (theme: Theme) => void
}

const themeStore = create<IThemeStore>((set) => ({
  theme: "light",
  setTheme: (theme) => set({ theme }),
}))

export default themeStore
