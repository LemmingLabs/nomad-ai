import { useSponsoredPlacesQuery } from '../../features/business/sponsored-places/model/sponsoredPlaces.hooks'
import { useBusinessAnalyticsOverviewQuery } from '../../features/business/analytics/model/businessAnalytics.hooks'
import { BusinessAnalyticsEmptyState } from '../../features/business/analytics/ui/BusinessAnalyticsEmptyState'
import { BusinessAnalyticsInteractionsChart } from '../../features/business/analytics/ui/BusinessAnalyticsInteractionsChart'
import { BusinessAnalyticsOverviewCards } from '../../features/business/analytics/ui/BusinessAnalyticsOverviewCards'
import { BusinessAnalyticsPlacesList } from '../../features/business/analytics/ui/BusinessAnalyticsPlacesList'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'
import { SectionCard } from '../../shared/ui/SectionCard'

export function BusinessAnalyticsPage() {
  const overviewQuery = useBusinessAnalyticsOverviewQuery()
  const placesQuery = useSponsoredPlacesQuery()

  const isLoading = overviewQuery.isLoading || placesQuery.isLoading

  if (isLoading) {
    return <PageLoadingState message="Loading analytics..." />
  }

  if (overviewQuery.isError || placesQuery.isError) {
    const err = overviewQuery.isError ? overviewQuery.error : placesQuery.error
    return (
      <PageErrorState
        title="Analytics"
        message={getErrorMessage(err, 'Failed to load analytics')}
        onRetry={() => {
          void overviewQuery.refetch()
          void placesQuery.refetch()
        }}
      />
    )
  }

  const overview =
    overviewQuery.data ?? ({
      impressions_count: 0,
      interactions_count: 0,
      interactions_by_type: {},
    } as const)
  const places = placesQuery.data ?? []

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Analytics</h1>
        <p className="text-sm text-neutral-600">
          Track impressions and interactions for your sponsored places.
        </p>
      </header>

      <section className="space-y-4">
        <BusinessAnalyticsOverviewCards overview={overview} />

        <SectionCard title="Interaction breakdown">
          <BusinessAnalyticsInteractionsChart
            interactionsByType={overview.interactions_by_type}
          />
        </SectionCard>
      </section>

      {places.length === 0 ? (
        <BusinessAnalyticsEmptyState />
      ) : (
        <section className="space-y-4">
          <h2 className="text-base font-semibold">By sponsored place</h2>
          <BusinessAnalyticsPlacesList places={places} />
        </section>
      )}
    </div>
  )
}
