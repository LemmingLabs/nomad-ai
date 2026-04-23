import axios from 'axios'

import { apiClient } from '../../../../shared/api/client'
import type {
  BusinessProfile,
  BusinessProfileUpsertPayload,
} from '../model/businessProfile.types'

export const businessProfileApi = {
  async getBusinessProfile(): Promise<BusinessProfile | null> {
    try {
      const { data } = await apiClient.get<BusinessProfile>('/business/me')
      return data
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null
      }
      throw error
    }
  },

  async createBusinessProfile(payload: BusinessProfileUpsertPayload) {
    const { data } = await apiClient.post<BusinessProfile>('/business/me', payload)
    return data
  },

  async updateBusinessProfile(payload: Partial<BusinessProfileUpsertPayload>) {
    const { data } = await apiClient.patch<BusinessProfile>('/business/me', payload)
    return data
  },
}

