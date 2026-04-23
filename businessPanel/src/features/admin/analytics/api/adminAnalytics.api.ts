import { apiClient } from '../../../../shared/api/client'
import type { AdminAnalyticsMetrics } from '../model/adminAnalytics.types'

export const adminAnalyticsApi = {
  async getAdminBusinessAnalytics(businessId: number) {
    const { data } = await apiClient.get<AdminAnalyticsMetrics>(
      `/admin/analytics/businesses/${businessId}`,
    )
    return data
  },

  async getAdminSponsoredPlaceAnalytics(placeId: number) {
    const { data } = await apiClient.get<AdminAnalyticsMetrics>(
      `/admin/analytics/sponsored-places/${placeId}`,
    )
    return data
  },
}

