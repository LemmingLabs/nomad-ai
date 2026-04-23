import { apiClient } from '../../../../shared/api/client'
import type {
  CreateSponsoredPlacePayload,
  SponsoredPlace,
  UpdateSponsoredPlacePayload,
} from '../model/sponsoredPlaces.types'

export const sponsoredPlacesApi = {
  async getSponsoredPlaces() {
    const { data } = await apiClient.get<SponsoredPlace[]>(
      '/business/me/sponsored-places',
    )
    return data
  },

  async createSponsoredPlace(payload: CreateSponsoredPlacePayload) {
    const { data } = await apiClient.post<SponsoredPlace>(
      '/business/me/sponsored-places',
      payload,
    )
    return data
  },

  async updateSponsoredPlace(id: number, payload: UpdateSponsoredPlacePayload) {
    const { data } = await apiClient.patch<SponsoredPlace>(
      `/business/me/sponsored-places/${id}`,
      payload,
    )
    return data
  },

  async deleteSponsoredPlace(id: number) {
    await apiClient.delete(`/business/me/sponsored-places/${id}`)
  },
}

