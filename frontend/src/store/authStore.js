import { create } from 'zustand'
import { authApi, usersApi } from '../api/services'

const useAuthStore = create((set, get) => ({
  user: null,
  role: localStorage.getItem('role') || null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,

  login: async (email, password) => {
    set({ isLoading: true, error: null })
    try {
      const { data } = await authApi.login({ email, password })
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      localStorage.setItem('role', data.role)
      set({ role: data.role, isAuthenticated: true, isLoading: false })
      return data.role
    } catch (err) {
      set({ error: err.response?.data?.detail || 'Login failed', isLoading: false })
      throw err
    }
  },

  logout: () => {
    authApi.logout()
    set({ user: null, role: null, isAuthenticated: false })
  },

  fetchMe: async () => {
    try {
      const { data } = await usersApi.getMe()
      set({ user: data })
    } catch {
      get().logout()
    }
  },

  clearError: () => set({ error: null }),
}))

export default useAuthStore
