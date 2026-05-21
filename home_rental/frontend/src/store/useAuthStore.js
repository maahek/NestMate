import { create } from 'zustand'
import api from '../api/axios'

const useAuthStore = create((set) => ({
  user:    null,
  loading: false,

  login: async (email, password) => {
    set({ loading: true })
    try {
      const res = await api.post('/accounts/login/', { email, password })
      set({ user: res.data.user, loading: false })
      return { success: true }
    } catch (err) {
      set({ loading: false })
      return {
        success: false,
        error: err.response?.data?.error || 'Login failed',
      }
    }
  },

  logout: async () => {
    try {
      await api.post('/accounts/logout/')
    } catch { /* silent */ }
    set({ user: null })
  },

  register: async (data) => {
    set({ loading: true })
    try {
      const res = await api.post('/accounts/register/', data)
      set({ user: res.data.user, loading: false })
      return { success: true }
    } catch (err) {
      set({ loading: false })
      const errData = err.response?.data
      return {
        success: false,
        error: errData?.error || errData || 'Registration failed',
      }
    }
  },

  fetchProfile: async () => {
    try {
      const res  = await api.get('/accounts/profile/')
      const data = res.data

      if (data.avatar_url && !data.avatar_url.startsWith('http')) {
        data.avatar_url = `http://localhost:8000${data.avatar_url}`
      }

      set({ user: data })
      return data
    } catch {
      // 401 = not logged in (normal) — don't show error
      // Any other error = silent fail
      set({ user: null })
      return null
    }
  },
}))
export default useAuthStore