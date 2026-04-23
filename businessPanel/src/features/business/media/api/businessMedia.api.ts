import { apiClient } from '../../../../shared/api/client'
import type { BusinessMedia, CreateBusinessMediaPayload } from '../model/businessMedia.types'

export const businessMediaApi = {
  async getBusinessMedia() {
    const { data } = await apiClient.get<BusinessMedia[]>('/business/me/media')
    return data
  },

  async createBusinessMedia(payload: CreateBusinessMediaPayload) {
    const { data } = await apiClient.post<BusinessMedia>('/business/me/media', payload)
    return data
  },

  async deleteBusinessMedia(mediaId: number) {
    await apiClient.delete(`/business/me/media/${mediaId}`)
  },
}

