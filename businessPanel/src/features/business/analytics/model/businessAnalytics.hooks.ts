import { useQuery } from '@tanstack/react-query'

import { queryKeys } from '../../../../shared/api'
import { businessAnalyticsApi } from '../api/businessAnalytics.api'

export function useBusinessAnalyticsOverviewQuery() {
  return useQuery({
    queryKey: queryKeys.business.analyticsOverview,
    queryFn: () => businessAnalyticsApi.getBusinessAnalyticsOverview(),
  })
}

export function useBusinessSponsoredPlaceAnalyticsQuery(
  placeId: number,
  enabled = true,
) {
  return useQuery({
    queryKey: queryKeys.business.sponsoredPlaceAnalytics(placeId),
    queryFn: () => businessAnalyticsApi.getBusinessSponsoredPlaceAnalytics(placeId),
    enabled: enabled && Number.isFinite(placeId),
  })
}

