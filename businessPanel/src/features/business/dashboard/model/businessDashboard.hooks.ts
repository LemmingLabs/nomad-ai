import { useMemo } from 'react'

import { useBusinessAnalyticsOverviewQuery } from '../../analytics/model/businessAnalytics.hooks'
import type { BusinessAnalyticsOverview } from '../../analytics/model/businessAnalytics.types'
import { useBusinessProfileQuery } from '../../profile/model/businessProfile.hooks'
import { useSponsoredPlacesQuery } from '../../sponsored-places/model/sponsoredPlaces.hooks'

export type SponsoredPlacesSummary = {
  total: number
  active: number
  pending: number
  inactive: number
}

const emptyOverview: BusinessAnalyticsOverview = {
  impressions_count: 0,
  interactions_count: 0,
  interactions_by_type: {},
}

export function useBusinessDashboardData() {
  const profileQuery = useBusinessProfileQuery()
  const placesQuery = useSponsoredPlacesQuery()
  const analyticsOverviewQuery = useBusinessAnalyticsOverviewQuery()

  const isLoading =
    profileQuery.isLoading || placesQuery.isLoading || analyticsOverviewQuery.isLoading

  const isError = profileQuery.isError || placesQuery.isError || analyticsOverviewQuery.isError

  const error = profileQuery.isError
    ? profileQuery.error
    : placesQuery.isError
      ? placesQuery.error
      : analyticsOverviewQuery.isError
        ? analyticsOverviewQuery.error
        : null

  const sponsoredSummary = useMemo((): SponsoredPlacesSummary => {
    const places = placesQuery.data ?? []
    const total = places.length
    const active = places.filter((p) => p.is_active).length
    const pending = places.filter((p) => !p.is_approved).length
    const inactive = places.filter((p) => !p.is_active).length

    return { total, active, pending, inactive }
  }, [placesQuery.data])

  const analyticsOverview = analyticsOverviewQuery.data ?? emptyOverview

  const refetchAll = () => {
    void profileQuery.refetch()
    void placesQuery.refetch()
    void analyticsOverviewQuery.refetch()
  }

  return {
    isLoading,
    isError,
    error,
    refetchAll,
    profile: profileQuery.data ?? null,
    sponsoredSummary,
    analyticsOverview,
  }
}

