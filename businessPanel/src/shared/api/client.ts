import axios, { type AxiosInstance } from 'axios'

import { authStorage } from '../../features/auth/model/auth.storage'
import { env } from '../config/env'

export const AUTH_UNAUTHORIZED_EVENT = 'nomadai:auth:unauthorized'

export const apiClient: AxiosInstance = axios.create({
  baseURL: env.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.request.use((config) => {
  const accessToken = authStorage.getAccessToken()
  if (accessToken) {
    config.headers = config.headers ?? {}
    config.headers.Authorization = `Bearer ${accessToken}`
  }
  return config
})

apiClient.interceptors.response.use(
  (response) => response,
  (error: unknown) => {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      authStorage.clearTokens()
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT))
      }
    }

    return Promise.reject(error)
  },
)

