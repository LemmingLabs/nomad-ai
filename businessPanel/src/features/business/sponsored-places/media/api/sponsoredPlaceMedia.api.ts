import { apiClient } from '../../../../../shared/api/client'

import type {
  SponsoredPlaceMedia,
  SponsoredPlaceMediaType,
} from '../model/sponsoredPlaceMedia.types'

export const sponsoredPlaceMediaApi = {
  async getSponsoredPlaceMedia(placeId: number) {
    const { data } = await apiClient.get<SponsoredPlaceMedia[]>(
      `/business/me/sponsored-places/${placeId}/media`,
    )
    return data
  },

  async uploadSponsoredPlaceMedia(
    placeId: number,
    file: File,
    type: SponsoredPlaceMediaType = 'image',
  ) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('type', type)

    const { data } = await apiClient.post<SponsoredPlaceMedia>(
      `/business/me/sponsored-places/${placeId}/media`,
      formData,
    )
    return data
  },

  async deleteSponsoredPlaceMedia(placeId: number, mediaId: number) {
    await apiClient.delete(
      `/business/me/sponsored-places/${placeId}/media/${mediaId}`,
    )
  },
}
