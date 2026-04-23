import { useEffect, useRef } from 'react'

import { authApi } from '../api/auth.api'
import { useAuthStore } from '../model/auth.store'
import { authStorage } from '../model/auth.storage'
import { AUTH_UNAUTHORIZED_EVENT } from '../../../shared/api/client'

export function useAuthBootstrap() {
  const bootstrappedRef = useRef(false)

  useEffect(() => {
    if (bootstrappedRef.current) return
    bootstrappedRef.current = true

    const { setStatus, setUser, clearAuth } = useAuthStore.getState()

    const run = async () => {
      const accessToken = authStorage.getAccessToken()
      const refreshToken = authStorage.getRefreshToken()

      if (!accessToken) {
        setUser(null)
        setStatus('unauthenticated')
        return
      }

      setStatus('loading')

      try {
        const user = await authApi.getMe()
        setUser(user)
        setStatus('authenticated')
        return
      } catch {
        // fallthrough to refresh
      }

      if (!refreshToken) {
        clearAuth()
        return
      }

      try {
        const refreshed = await authApi.refresh(refreshToken)
        authStorage.setAccessToken(refreshed.accessToken)
        if (refreshed.refreshToken) {
          authStorage.setRefreshToken(refreshed.refreshToken)
        }

        const user = await authApi.getMe()
        setUser(user)
        setStatus('authenticated')
      } catch {
        clearAuth()
      }
    }

    void run()
  }, [])

  useEffect(() => {
    const handleUnauthorized = () => {
      useAuthStore.getState().clearAuth()
    }

    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized)
    return () => {
      window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized)
    }
  }, [])
}
