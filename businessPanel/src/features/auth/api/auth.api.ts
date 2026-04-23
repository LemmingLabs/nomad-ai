import { apiClient } from '../../../shared/api/client'
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  RefreshResponse,
} from '../model/auth.types'

type BackendTokenResponse = {
  access_token?: unknown
  refresh_token?: unknown
  accessToken?: unknown
  refreshToken?: unknown
  user?: unknown
}

function pickTokenString(value: unknown): string | null {
  if (typeof value !== 'string') return null
  const trimmed = value.trim()
  return trimmed === '' ? null : trimmed
}

export const authApi = {
  async login(payload: LoginRequest) {
    const { data } = await apiClient.post<BackendTokenResponse>('/auth/login', payload)
    const accessToken =
      pickTokenString(data.accessToken) ?? pickTokenString(data.access_token)
    const refreshToken =
      pickTokenString(data.refreshToken) ??
      pickTokenString(data.refresh_token) ??
      undefined

    if (!accessToken) {
      throw new Error('Invalid login response: missing access token')
    }

    return { accessToken, refreshToken, user: data.user as AuthUser | undefined } satisfies LoginResponse
  },

  async refresh(refreshToken: string) {
    const { data } = await apiClient.post<RefreshResponse>('/auth/refresh', {
      refreshToken,
    })
    return data
  },

  async getMe() {
    const { data } = await apiClient.get<AuthUser>('/auth/me')
    return data
  },
}
