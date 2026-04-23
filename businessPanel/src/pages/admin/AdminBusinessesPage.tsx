import { useEffect, useState } from 'react'

import {
  useAdminBusinessDetailsQuery,
  useAdminBusinessesQuery,
} from '../../features/admin/businesses/model/adminBusinesses.hooks'
import { AdminBusinessDetailsCard } from '../../features/admin/businesses/ui/AdminBusinessDetailsCard'
import { AdminBusinessesEmptyState } from '../../features/admin/businesses/ui/AdminBusinessesEmptyState'
import { AdminBusinessesTable } from '../../features/admin/businesses/ui/AdminBusinessesTable'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'
import { SectionCard } from '../../shared/ui/SectionCard'

export function AdminBusinessesPage() {
  const businessesQuery = useAdminBusinessesQuery()
  const [selectedBusinessId, setSelectedBusinessId] = useState<number | null>(null)

  const detailsQuery = useAdminBusinessDetailsQuery(
    selectedBusinessId ?? Number.NaN,
    selectedBusinessId != null,
  )

  useEffect(() => {
    if (!businessesQuery.data || businessesQuery.data.length === 0) return
    if (selectedBusinessId != null) return
    setSelectedBusinessId(businessesQuery.data[0].id)
  }, [businessesQuery.data, selectedBusinessId])

  if (businessesQuery.isLoading) {
    return <PageLoadingState message="Loading businesses..." />
  }

  if (businessesQuery.isError) {
    return (
      <PageErrorState
        title="Businesses"
        message={getErrorMessage(businessesQuery.error, 'Failed to load businesses')}
        onRetry={() => businessesQuery.refetch()}
      />
    )
  }

  const businesses = businessesQuery.data ?? []

  if (businesses.length === 0) {
    return (
      <div className="space-y-4">
        <header className="space-y-1">
          <h1 className="text-lg font-semibold">Businesses</h1>
          <p className="text-sm text-neutral-600">
            View business profiles registered in the system.
          </p>
        </header>
        <AdminBusinessesEmptyState />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Businesses</h1>
        <p className="text-sm text-neutral-600">
          View business profiles registered in the system.
        </p>
      </header>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <AdminBusinessesTable
            businesses={businesses}
            selectedBusinessId={selectedBusinessId}
            onSelect={setSelectedBusinessId}
          />
        </div>

        <div className="lg:col-span-1">
          {selectedBusinessId == null ? (
            <SectionCard>
              <p className="text-sm text-neutral-600">Select a business to view details.</p>
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
            <AdminBusinessDetailsCard business={detailsQuery.data} />
          )}
        </div>
      </div>
    </div>
  )
}
