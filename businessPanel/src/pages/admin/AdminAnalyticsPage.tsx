import { useEffect, useMemo, useState } from 'react'

import type { AdminAnalyticsMode } from '../../features/admin/analytics/model/adminAnalytics.types'
import {
  useAdminBusinessAnalyticsQuery,
  useAdminSponsoredPlaceAnalyticsQuery,
} from '../../features/admin/analytics/model/adminAnalytics.hooks'
import { AdminAnalyticsModeSwitcher } from '../../features/admin/analytics/ui/AdminAnalyticsModeSwitcher'
import { AdminAnalyticsSelectionPanel } from '../../features/admin/analytics/ui/AdminAnalyticsSelectionPanel'
import { AdminAnalyticsOverviewCards } from '../../features/admin/analytics/ui/AdminAnalyticsOverviewCards'
import { AdminAnalyticsInteractionsChart } from '../../features/admin/analytics/ui/AdminAnalyticsInteractionsChart'
import { AdminAnalyticsEmptyState } from '../../features/admin/analytics/ui/AdminAnalyticsEmptyState'
import { AdminAnalyticsDetailsCard } from '../../features/admin/analytics/ui/AdminAnalyticsDetailsCard'
import { useAdminBusinessesQuery } from '../../features/admin/businesses/model/adminBusinesses.hooks'
import type { AdminBusiness } from '../../features/admin/businesses/model/adminBusinesses.types'
import type { AdminSponsoredPlace } from '../../features/admin/sponsored-moderation/model/adminSponsoredModeration.types'
import { useAdminSponsoredPlacesQuery } from '../../features/admin/sponsored-moderation/model/adminSponsoredModeration.hooks'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'
import { SectionCard } from '../../shared/ui/SectionCard'

export function AdminAnalyticsPage() {
  const [mode, setMode] = useState<AdminAnalyticsMode>('business')
  const [selectedId, setSelectedId] = useState<number | null>(null)

  const businessesQuery = useAdminBusinessesQuery()
  const sponsoredPlacesQuery = useAdminSponsoredPlacesQuery({ preset: 'all' })

  useEffect(() => {
    setSelectedId(null)
  }, [mode])

  const selectionQuery = mode === 'business' ? businessesQuery : sponsoredPlacesQuery
  const selectionItems = selectionQuery.data ?? []

  useEffect(() => {
    if (selectedId != null) return
    if (selectionItems.length === 0) return
    setSelectedId(selectionItems[0].id)
  }, [selectionItems, selectedId])

  const selectedBusiness = useMemo(() => {
    if (mode !== 'business' || selectedId == null) return null
    return (selectionItems as AdminBusiness[]).find((b) => b.id === selectedId) ?? null
  }, [mode, selectedId, selectionItems])

  const selectedPlace = useMemo(() => {
    if (mode !== 'sponsoredPlace' || selectedId == null) return null
    return (
      (selectionItems as AdminSponsoredPlace[]).find((p) => p.id === selectedId) ?? null
    )
  }, [mode, selectedId, selectionItems])

  const businessAnalyticsQuery = useAdminBusinessAnalyticsQuery(
    selectedId ?? Number.NaN,
    mode === 'business' && selectedId != null,
  )

  const placeAnalyticsQuery = useAdminSponsoredPlaceAnalyticsQuery(
    selectedId ?? Number.NaN,
    mode === 'sponsoredPlace' && selectedId != null,
  )

  const analyticsQuery = mode === 'business' ? businessAnalyticsQuery : placeAnalyticsQuery

  if (selectionQuery.isLoading) {
    return <PageLoadingState message="Loading analytics..." />
  }

  if (selectionQuery.isError) {
    return (
      <PageErrorState
        title="Analytics"
        message={getErrorMessage(selectionQuery.error, 'Failed to load selection data')}
        onRetry={() => selectionQuery.refetch()}
      />
    )
  }

  return (
    <div className="space-y-6">
      <header className="space-y-2">
        <div className="flex items-start justify-between gap-4">
          <div className="space-y-1">
            <h1 className="text-lg font-semibold">Analytics</h1>
            <p className="text-sm text-neutral-600">
              View analytics for businesses and sponsored places.
            </p>
          </div>
          <AdminAnalyticsModeSwitcher value={mode} onChange={setMode} />
        </div>
      </header>

      {selectionItems.length === 0 ? (
        <AdminAnalyticsEmptyState
          title={mode === 'business' ? 'No businesses yet' : 'No sponsored places yet'}
          description="Add entities first to start tracking analytics."
        />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-1">
            {mode === 'business' ? (
              <AdminAnalyticsSelectionPanel
                mode="business"
                items={selectionItems as AdminBusiness[]}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            ) : (
              <AdminAnalyticsSelectionPanel
                mode="sponsoredPlace"
                items={selectionItems as AdminSponsoredPlace[]}
                selectedId={selectedId}
                onSelect={setSelectedId}
              />
            )}
          </div>

          <div className="space-y-6 lg:col-span-2">
            {selectedId == null ? (
              <SectionCard>
                <p className="text-sm text-neutral-600">Select an item to view analytics.</p>
              </SectionCard>
            ) : mode === 'business' && selectedBusiness ? (
              <AdminAnalyticsDetailsCard mode="business" business={selectedBusiness} />
            ) : mode === 'sponsoredPlace' && selectedPlace ? (
              <AdminAnalyticsDetailsCard mode="sponsoredPlace" place={selectedPlace} />
            ) : (
              <SectionCard>
                <p className="text-sm text-neutral-600">No details available.</p>
              </SectionCard>
            )}

            {selectedId != null ? (
              analyticsQuery.isLoading ? (
                <PageLoadingState message="Loading metrics..." />
              ) : analyticsQuery.isError ? (
                <SectionCard>
                  <p className="text-sm text-neutral-700">
                    {getErrorMessage(analyticsQuery.error, 'Failed to load metrics.')}
                  </p>
                  <button
                    type="button"
                    onClick={() => analyticsQuery.refetch()}
                    className="mt-4 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
                  >
                    Retry
                  </button>
                </SectionCard>
              ) : !analyticsQuery.data ? (
                <SectionCard>
                  <p className="text-sm text-neutral-600">No metrics available.</p>
                </SectionCard>
              ) : (
                <>
                  <AdminAnalyticsOverviewCards metrics={analyticsQuery.data} />
                  <SectionCard title="Interaction breakdown">
                    <AdminAnalyticsInteractionsChart
                      interactionsByType={analyticsQuery.data.interactions_by_type}
                    />
                  </SectionCard>
                </>
              )
            ) : null}
          </div>
        </div>
      )}
    </div>
  )
}
