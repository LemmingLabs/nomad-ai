import { useAdminDashboardData } from '../../features/admin/dashboard/model/adminDashboard.hooks'
import { AdminDashboardView } from '../../features/admin/dashboard/ui/AdminDashboardView'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'

export function AdminDashboardPage() {
  const { isLoading, isError, error, refetchAll, counts, recent } = useAdminDashboardData()

  if (isLoading) {
    return <PageLoadingState message="Loading dashboard..." />
  }

  if (isError) {
    return (
      <PageErrorState
        title="Dashboard"
        message={getErrorMessage(error, 'Failed to load dashboard')}
        onRetry={refetchAll}
      />
    )
  }

  return (
    <AdminDashboardView
      counts={counts}
      recentUsers={recent.recentUsers}
      recentBusinesses={recent.recentBusinesses}
    />
  )
}
