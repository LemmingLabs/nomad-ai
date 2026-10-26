import { apiClient } from '../../../shared/api'
import type { OfferSearchRequest, OffersUnavailableResponse } from '../model/types'

export const offersApi = {
  search: (request: OfferSearchRequest) =>
    apiClient
      .post<OffersUnavailableResponse>('/offers/search', request)
      .then((response) => response.data),
}
