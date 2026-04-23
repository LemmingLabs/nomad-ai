import { authStorage } from '../model/auth.storage'
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  RefreshResponse,
} from '../model/auth.types'

async function requestJson<TResponse>(
  path: string,
  init?: RequestInit,
): Promise<TResponse> {
  const res = await fetch(path, init)

  if (!res.ok) {
    throw new Error(`Request failed: ${res.status} ${res.statusText}`)
  }

  return (await res.json()) as TResponse
}

export const authApi = {
  login(payload: LoginRequest) {
    return requestJson<LoginResponse>('/api/v1/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },

  refresh(refreshToken: string) {
    return requestJson<RefreshResponse>('/api/v1/auth/refresh', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refreshToken }),
    })
  },

  getMe() {
    const accessToken = authStorage.getAccessToken()

    return requestJson<AuthUser>('/api/v1/auth/me', {
      method: 'GET',
      headers: accessToken
        ? { Authorization: `Bearer ${accessToken}` }
        : undefined,
    })
  },
}
