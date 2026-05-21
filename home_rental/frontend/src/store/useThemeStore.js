import { create } from 'zustand'

const useThemeStore = create((set) => ({
  theme: localStorage.getItem('nestmate-theme') || 'light',

  toggleTheme: () => {
    set((state) => {
      const next = state.theme === 'light' ? 'dark' : 'light'
      localStorage.setItem('nestmate-theme', next)
      document.documentElement.setAttribute('data-theme', next)
      return { theme: next }
    })
  },

  initTheme: () => {
    const saved   = localStorage.getItem('nestmate-theme')
    const system  = window.matchMedia('(prefers-color-scheme: dark)').matches
                    ? 'dark' : 'light'
    const theme   = saved || system
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('nestmate-theme', theme)
    set({ theme })
  },
}))

export default useThemeStore