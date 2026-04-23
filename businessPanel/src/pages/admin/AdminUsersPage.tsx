import { useEffect, useState } from 'react'

import { useAuthStore } from '../../features/auth/model/auth.store'
import { useAdminUserDetailsQuery, useAdminUsersQuery } from '../../features/admin/users/model/adminUsers.hooks'
import { AdminUsersEmptyState } from '../../features/admin/users/ui/AdminUsersEmptyState'
import { AdminUsersTable } from '../../features/admin/users/ui/AdminUsersTable'
import { AdminUserDetailsCard } from '../../features/admin/users/ui/AdminUserDetailsCard'
import { AdminUserRoleForm } from '../../features/admin/users/ui/AdminUserRoleForm'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'
import { SectionCard } from '../../shared/ui/SectionCard'

export function AdminUsersPage() {
  const currentAdminId = useAuthStore((s) => s.user?.id ?? null)

  const usersQuery = useAdminUsersQuery()
  const [selectedUserId, setSelectedUserId] = useState<number | null>(null)

  const detailsQuery = useAdminUserDetailsQuery(
    selectedUserId ?? Number.NaN,
    selectedUserId != null,
  )

  useEffect(() => {
    if (!usersQuery.data || usersQuery.data.length === 0) return
    if (selectedUserId != null) return
    setSelectedUserId(usersQuery.data[0].id)
  }, [usersQuery.data, selectedUserId])

  if (usersQuery.isLoading) {
    return <PageLoadingState message="Loading users..." />
  }

  if (usersQuery.isError) {
    return (
      <PageErrorState
        title="Users"
        message={getErrorMessage(usersQuery.error, 'Failed to load users')}
        onRetry={() => usersQuery.refetch()}
      />
    )
  }

  const users = usersQuery.data ?? []

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Users</h1>
        <p className="text-sm text-neutral-600">
          Manage user roles and access levels. Business role does not auto-create a business profile.
        </p>
      </header>

      {users.length === 0 ? (
        <AdminUsersEmptyState />
      ) : (
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2">
            <AdminUsersTable users={users} selectedUserId={selectedUserId} onSelect={setSelectedUserId} />
          </div>

          <div className="space-y-6 lg:col-span-1">
            {selectedUserId == null ? (
              <SectionCard>
                <p className="text-sm text-neutral-600">Select a user to view details.</p>
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
              <>
                <AdminUserDetailsCard user={detailsQuery.data} />
                <AdminUserRoleForm user={detailsQuery.data} currentAdminId={currentAdminId} />
              </>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

