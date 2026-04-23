import { apiClient } from '../../../../shared/api/client'
import type { AdminBusiness, AdminBusinessDetails } from '../model/adminBusinesses.types'

export const adminBusinessesApi = {
  async getAdminBusinesses() {
    const { data } = await apiClient.get<AdminBusiness[]>('/admin/businesses')
    return data
  },

  async getAdminBusinessDetails(businessId: number) {
    const { data } = await apiClient.get<AdminBusinessDetails>(
      `/admin/businesses/${businessId}`,
    )
    return data
  },
}

