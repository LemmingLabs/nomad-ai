import { useBusinessDashboardData } from '../../features/business/dashboard/model/businessDashboard.hooks'
import { BusinessDashboardView } from '../../features/business/dashboard/ui/BusinessDashboardView'
import { getErrorMessage } from '../../shared/lib/getErrorMessage'
import { PageErrorState } from '../../shared/ui/PageErrorState'
import { PageLoadingState } from '../../shared/ui/PageLoadingState'

export function BusinessDashboardPage() {
  const { isLoading, isError, error, refetchAll, profile, sponsoredSummary, analyticsOverview } =
    useBusinessDashboardData()

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
    <BusinessDashboardView
      profile={profile}
      sponsoredSummary={sponsoredSummary}
      analyticsOverview={analyticsOverview}
    />
  )
}
