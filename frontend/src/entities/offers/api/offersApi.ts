import { apiClient } from '../../../shared/api'
import type { OfferSearchRequest, OffersSearchResponse } from '../model/types'

export const offersApi = {
  search: (request: OfferSearchRequest) =>
    apiClient
      .post<OffersSearchResponse>('/offers/search', request)
      .then((response) => response.data),
}
