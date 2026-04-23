import { useNavigate } from 'react-router-dom'

import type { BusinessProfile } from '../../profile/model/businessProfile.types'
import type { BusinessAnalyticsOverview } from '../../analytics/model/businessAnalytics.types'
import { BusinessAnalyticsOverviewCards } from '../../analytics/ui/BusinessAnalyticsOverviewCards'
import type { SponsoredPlacesSummary } from '../model/businessDashboard.hooks'
import { DashboardGrid } from '../../../../shared/ui/dashboard/DashboardGrid'
import { DashboardStatCard } from '../../../../shared/ui/dashboard/DashboardStatCard'
import { SectionCard } from '../../../../shared/ui/SectionCard'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'

type BusinessDashboardViewProps = {
  profile: BusinessProfile | null
  sponsoredSummary: SponsoredPlacesSummary
  analyticsOverview: BusinessAnalyticsOverview
}

function ProfileStatusCard({ profile }: { profile: BusinessProfile | null }) {
  const navigate = useNavigate()

  const hasProfile = profile != null
  const isActive = profile?.is_active !== false

  const badge = !hasProfile ? (
    <StatusBadge variant="neutral">Not created</StatusBadge>
  ) : isActive ? (
    <StatusBadge variant="success">Active</StatusBadge>
  ) : (
    <StatusBadge variant="warning">Inactive</StatusBadge>
  )

  return (
    <SectionCard
      title="Profile status"
      description="Keep your profile up to date so customers can find you."
      actions={
        <button
          type="button"
          onClick={() => navigate('/business/profile')}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
        >
          {hasProfile ? 'Edit profile' : 'Create business profile'}
        </button>
      }
    >
      <div className="space-y-3">
        <div className="flex items-center justify-between gap-4">
          <div className="text-sm text-neutral-600">Status</div>
          {badge}
        </div>

        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          <div>
            <div className="text-xs text-neutral-500">Name</div>
            <div className="mt-1 text-sm font-medium text-neutral-900">
              {profile?.name ?? '—'}
            </div>
          </div>
          <div>
            <div className="text-xs text-neutral-500">Website</div>
            <div className="mt-1 text-sm font-medium text-neutral-900">
              {profile?.website_url ?? '—'}
            </div>
          </div>
        </div>
      </div>
    </SectionCard>
  )
}

function SponsoredPlacesSummaryCard({ summary }: { summary: SponsoredPlacesSummary }) {
  const navigate = useNavigate()

  return (
    <SectionCard
      title="Sponsored places"
      description="Summary of your sponsored places."
      actions={
        <button
          type="button"
          onClick={() => navigate('/business/sponsored-places')}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
        >
          Manage
        </button>
      }
    >
      <DashboardGrid className="grid-cols-1 md:grid-cols-2">
        <DashboardStatCard label="Total" value={summary.total} />
        <DashboardStatCard label="Active" value={summary.active} />
        <DashboardStatCard label="Pending approval" value={summary.pending} />
        <DashboardStatCard label="Inactive" value={summary.inactive} />
      </DashboardGrid>
    </SectionCard>
  )
}

function AnalyticsSummaryCard({ overview }: { overview: BusinessAnalyticsOverview }) {
  const navigate = useNavigate()

  return (
    <SectionCard
      title="Analytics summary"
      description="Impressions, interactions and CTR."
      actions={
        <button
          type="button"
          onClick={() => navigate('/business/analytics')}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
        >
          View analytics
        </button>
      }
    >
      <BusinessAnalyticsOverviewCards overview={overview} />
    </SectionCard>
  )
}

function QuickActionsCard() {
  const navigate = useNavigate()

  const actions = [
    { label: 'Edit Profile', to: '/business/profile', variant: 'primary' as const },
    { label: 'Manage Media', to: '/business/media', variant: 'secondary' as const },
    {
      label: 'Create Sponsored Place',
      to: '/business/sponsored-places',
      variant: 'secondary' as const,
    },
    { label: 'View Analytics', to: '/business/analytics', variant: 'secondary' as const },
  ]

  return (
    <SectionCard title="Quick actions" description="Jump to the most used workflows.">
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
        {actions.map((a) => (
          <button
            key={a.to}
            type="button"
            onClick={() => navigate(a.to)}
            className={[
              'rounded-md px-4 py-2 text-sm font-medium',
              a.variant === 'primary'
                ? 'bg-neutral-900 text-white hover:bg-neutral-800'
                : 'border border-neutral-200 bg-white hover:bg-neutral-50',
            ].join(' ')}
          >
            {a.label}
          </button>
        ))}
      </div>
    </SectionCard>
  )
}

export function BusinessDashboardView({
  profile,
  sponsoredSummary,
  analyticsOverview,
}: BusinessDashboardViewProps) {
  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Dashboard</h1>
        <p className="text-sm text-neutral-600">
          Overview of your business settings, places and analytics.
        </p>
      </header>

      <DashboardGrid className="grid-cols-1 md:grid-cols-2">
        <ProfileStatusCard profile={profile} />
        <SponsoredPlacesSummaryCard summary={sponsoredSummary} />
      </DashboardGrid>

      <DashboardGrid className="grid-cols-1 md:grid-cols-2">
        <AnalyticsSummaryCard overview={analyticsOverview} />
        <QuickActionsCard />
      </DashboardGrid>
    </div>
  )
}

