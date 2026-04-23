import { apiClient } from '../../../../shared/api'
import type { AdminUser, AdminUserDetails, UpdateUserRolePayload } from '../model/adminUsers.types'

export const adminUsersApi = {
  async getAdminUsers() {
    const { data } = await apiClient.get<AdminUser[]>('/admin/users')
    return data
  },

  async getAdminUserDetails(userId: number) {
    const { data } = await apiClient.get<AdminUserDetails>(`/admin/users/${userId}`)
    return data
  },

  async updateAdminUserRole(userId: number, payload: UpdateUserRolePayload) {
    const { data } = await apiClient.patch<AdminUserDetails>(
      `/admin/users/${userId}/role`,
      payload,
    )
    return data
  },
}

