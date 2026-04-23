import { useEffect, useState } from 'react'

import type { AdminSponsoredPlaceListFilters } from '../../features/admin/sponsored-moderation/model/adminSponsoredModeration.types'
import {
  useAdminSponsoredPlaceDetailsQuery,
  useAdminSponsoredPlacesQuery,
} from '../../features/admin/sponsored-moderation/model/adminSponsoredModeration.hooks'
import { AdminSponsoredModerationEmptyState } from '../../features/admin/sponsored-moderation/ui/AdminSponsoredModerationEmptyState'
import { AdminSponsoredModerationFilters } from '../../features/admin/sponsored-moderation/ui/AdminSponsoredModerationFilters'
import { AdminSponsoredPlaceDetailsCard } from '../../features/admin/sponsored-moderation/ui/AdminSponsoredPlaceDetailsCard'
import { AdminSponsoredPlacesTable } from '../../features/admin/sponsored-moderation/ui/AdminSponsoredPlacesTable'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'
import { SectionCard } from '../../shared/ui/SectionCard'

const defaultFilters: AdminSponsoredPlaceListFilters = { preset: 'pending' }

export function AdminModerationPage() {
  const [filters, setFilters] = useState<AdminSponsoredPlaceListFilters>(defaultFilters)
  const placesQuery = useAdminSponsoredPlacesQuery(filters)

  const [selectedPlaceId, setSelectedPlaceId] = useState<number | null>(null)

  const detailsQuery = useAdminSponsoredPlaceDetailsQuery(
    selectedPlaceId ?? Number.NaN,
    selectedPlaceId != null,
  )

  useEffect(() => {
    setSelectedPlaceId(null)
  }, [filters.preset])

  useEffect(() => {
    if (!placesQuery.data || placesQuery.data.length === 0) return
    if (selectedPlaceId != null) return
    setSelectedPlaceId(placesQuery.data[0].id)
  }, [placesQuery.data, selectedPlaceId])

  if (placesQuery.isLoading) {
    return <PageLoadingState message="Loading sponsored places..." />
  }

  if (placesQuery.isError) {
    return (
      <PageErrorState
        title="Sponsored moderation"
        message={getErrorMessage(placesQuery.error, 'Failed to load sponsored places')}
        onRetry={() => placesQuery.refetch()}
      />
    )
  }

  const places = placesQuery.data ?? []

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Sponsored moderation</h1>
        <p className="text-sm text-neutral-600">
          Review sponsored places and apply moderation actions.
        </p>
      </header>

      <AdminSponsoredModerationFilters value={filters} onChange={setFilters} />

      {places.length === 0 ? (
        <AdminSponsoredModerationEmptyState />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <AdminSponsoredPlacesTable
              places={places}
              selectedPlaceId={selectedPlaceId}
              onSelect={setSelectedPlaceId}
            />
          </div>

          <div className="lg:col-span-1">
            {selectedPlaceId == null ? (
              <SectionCard>
                <p className="text-sm text-neutral-600">
                  Select a sponsored place to view details.
                </p>
              </SectionCard>
            ) : detailsQuery.isLoading ? (
              <SectionCard>
                <PageLoadingState message="Loading details..." />
              </SectionCard>
            ) : detailsQuery.isError ? (
              <SectionCard>
                <p className="text-sm text-neutral-700">
                  {getErrorMessage(detailsQuery.error, 'Failed to load details.')}
                </p>
                <button
                  type="button"
                  onClick={() => detailsQuery.refetch()}
                  className="mt-4 rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
                >
                  Retry
                </button>
              </SectionCard>
            ) : !detailsQuery.data ? (
              <SectionCard>
                <p className="text-sm text-neutral-600">No details available.</p>
              </SectionCard>
            ) : (
              <AdminSponsoredPlaceDetailsCard place={detailsQuery.data} />
            )}
          </div>
        </div>
      )}
    </div>
  )
}
