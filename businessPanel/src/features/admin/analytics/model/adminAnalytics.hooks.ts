import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { adminAnalyticsApi } from '../api/adminAnalytics.api'

export function useAdminBusinessAnalyticsQuery(businessId: number, enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.analytics.business(businessId),
    queryFn: () => adminAnalyticsApi.getAdminBusinessAnalytics(businessId),
    enabled: enabled && Number.isFinite(businessId),
  })
}

export function useAdminSponsoredPlaceAnalyticsQuery(placeId: number, enabled = true) {
  return useQuery({
    queryKey: queryKeys.admin.analytics.sponsoredPlace(placeId),
    queryFn: () => adminAnalyticsApi.getAdminSponsoredPlaceAnalytics(placeId),
    enabled: enabled && Number.isFinite(placeId),
  })
}

