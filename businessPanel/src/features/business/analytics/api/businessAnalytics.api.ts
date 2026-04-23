import { apiClient } from '../../../../shared/api/client'
import type {
  BusinessAnalyticsOverview,
  BusinessPlaceAnalytics,
} from '../model/businessAnalytics.types'

export const businessAnalyticsApi = {
  async getBusinessAnalyticsOverview() {
    const { data } = await apiClient.get<BusinessAnalyticsOverview>(
      '/business/me/analytics/overview',
    )
    return data
  },

  async getBusinessSponsoredPlaceAnalytics(placeId: number) {
    const { data } = await apiClient.get<BusinessPlaceAnalytics>(
      `/business/me/analytics/sponsored-places/${placeId}`,
    )
    return data
  },
}

