import { create } from 'zustand'

import { authApi } from '../api/auth.api'
import { authStorage } from './auth.storage'
import type { AuthState, AuthStatus, AuthUser, LoginRequest } from './auth.types'

type AuthActions = {
  setUser: (user: AuthUser | null) => void
  setStatus: (status: AuthStatus) => void
  clearAuth: () => void
  login: (payload: LoginRequest) => Promise<void>
  logout: () => void
}

type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>((set, get) => ({
  status: 'idle',
  user: null,

  setUser(user) {
    set({ user })
  },

  setStatus(status) {
    set({ status })
  },

  clearAuth() {
    authStorage.clearTokens()
    set({ user: null, status: 'unauthenticated' })
  },

  async login(payload) {
    const { setStatus, setUser, clearAuth } = get()

    setStatus('loading')
    try {
      const res = await authApi.login(payload)
      authStorage.setTokensOptional({ accessToken: res.accessToken, refreshToken: res.refreshToken })

      if (res.user) {
        setUser(res.user)
        setStatus('authenticated')
        return
      }

      const user = await authApi.getMe()
      setUser(user)
      setStatus('authenticated')
    } catch (error) {
      clearAuth()
      throw error
    }
  },

  logout() {
    get().clearAuth()
  },
}))
