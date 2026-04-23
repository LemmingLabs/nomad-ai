import type { SponsoredPlace } from '../../sponsored-places/model/sponsoredPlaces.types'
import { useBusinessSponsoredPlaceAnalyticsQuery } from '../model/businessAnalytics.hooks'
import { calculateCTR, formatCTR } from '../model/businessAnalytics.utils'
import { BusinessAnalyticsInteractionsChart } from './BusinessAnalyticsInteractionsChart'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'

type BusinessAnalyticsPlaceCardProps = {
  place: SponsoredPlace
}

export function BusinessAnalyticsPlaceCard({ place }: BusinessAnalyticsPlaceCardProps) {
  const analyticsQuery = useBusinessSponsoredPlaceAnalyticsQuery(place.id, true)

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4">
      <header className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-neutral-900">{place.title}</div>
          <div className="mt-1 text-sm text-neutral-700">
            {place.city} • {place.category}
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge variant={place.is_approved ? 'success' : 'warning'}>
              {place.is_approved ? 'Approved' : 'Pending'}
            </StatusBadge>
            <StatusBadge variant={place.is_active ? 'success' : 'neutral'}>
              {place.is_active ? 'Active' : 'Inactive'}
            </StatusBadge>
          </div>
        </div>
      </header>

      <div className="mt-4">
        {analyticsQuery.isLoading ? (
          <div className="text-sm text-neutral-600">Loading analytics...</div>
        ) : analyticsQuery.isError ? (
          <div className="flex items-center justify-between gap-4">
            <div className="text-sm text-neutral-700">Failed to load analytics.</div>
            <button
              type="button"
              onClick={() => analyticsQuery.refetch()}
              className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
            >
              Retry
            </button>
          </div>
        ) : (
          (() => {
            const metrics =
              analyticsQuery.data ?? ({
                impressions_count: 0,
                interactions_count: 0,
                interactions_by_type: {},
              } as const)
            const ctr = calculateCTR(
              metrics.interactions_count,
              metrics.impressions_count,
            )

            return (
              <div className="space-y-4">
                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-md bg-neutral-50 p-3">
                    <div className="text-xs text-neutral-500">Impressions</div>
                    <div className="mt-1 text-sm font-semibold">
                      {metrics.impressions_count}
                    </div>
                  </div>
                  <div className="rounded-md bg-neutral-50 p-3">
                    <div className="text-xs text-neutral-500">Interactions</div>
                    <div className="mt-1 text-sm font-semibold">
                      {metrics.interactions_count}
                    </div>
                  </div>
                  <div className="rounded-md bg-neutral-50 p-3">
                    <div className="text-xs text-neutral-500">CTR</div>
                    <div className="mt-1 text-sm font-semibold">
                      {formatCTR(ctr)}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="text-xs font-medium text-neutral-600">
                    Interaction breakdown
                  </div>
                  <div className="mt-2">
                    <BusinessAnalyticsInteractionsChart
                      interactionsByType={metrics.interactions_by_type}
                      height={160}
                    />
                  </div>
                </div>
              </div>
            )
          })()
        )}
      </div>
    </section>
  )
}
