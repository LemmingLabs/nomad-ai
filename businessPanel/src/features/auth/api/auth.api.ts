import { apiClient } from '../../../shared/api/client'
import type {
  AuthUser,
  LoginRequest,
  LoginResponse,
  RefreshResponse,
} from '../model/auth.types'

export const authApi = {
  async login(payload: LoginRequest) {
    const { data } = await apiClient.post<LoginResponse>('/auth/login', payload)
    return data
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
