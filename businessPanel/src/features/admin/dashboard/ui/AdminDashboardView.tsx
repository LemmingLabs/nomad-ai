import { useNavigate } from 'react-router-dom'

import type { AdminBusiness } from '../../businesses/model/adminBusinesses.types'
import type { AdminUser } from '../../users/model/adminUsers.types'
import { formatDateTime } from '../../../../shared/lib/formatDateTime'
import { DashboardGrid } from '../../../../shared/ui/dashboard/DashboardGrid'
import { DashboardStatCard } from '../../../../shared/ui/dashboard/DashboardStatCard'
import { SectionCard } from '../../../../shared/ui/SectionCard'

type AdminDashboardCounts = {
  usersCount: number
  businessesCount: number
  sponsoredPlacesCount: number
  pendingModerationCount: number
  activeSubscriptionPlansCount: number
  inactiveSubscriptionPlansCount: number
}

type AdminDashboardViewProps = {
  counts: AdminDashboardCounts
  recentUsers: AdminUser[]
  recentBusinesses: AdminBusiness[]
}

function QuickActionsCard() {
  const navigate = useNavigate()

  const actions = [
    { label: 'Manage Users', to: '/admin/users', variant: 'primary' as const },
    { label: 'Review Moderation', to: '/admin/sponsored-moderation', variant: 'secondary' as const },
    { label: 'View Businesses', to: '/admin/businesses', variant: 'secondary' as const },
    {
      label: 'Manage Subscription Plans',
      to: '/admin/subscription-plans',
      variant: 'secondary' as const,
    },
    { label: 'View Analytics', to: '/admin/analytics', variant: 'secondary' as const },
  ]

  return (
    <SectionCard title="Quick actions" description="Jump to key admin workflows.">
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

function NeedsAttentionCard({ counts }: { counts: AdminDashboardCounts }) {
  const navigate = useNavigate()

  return (
    <SectionCard
      title="Needs attention"
      description="Items that may require action."
      actions={
        <button
          type="button"
          onClick={() => navigate('/admin/sponsored-moderation')}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
        >
          Review
        </button>
      }
    >
      <div className="space-y-3 text-sm text-neutral-700">
        <div className="flex items-center justify-between gap-4">
          <div>Pending sponsored places</div>
          <div className="font-semibold text-neutral-900">{counts.pendingModerationCount}</div>
        </div>
        <div className="flex items-center justify-between gap-4">
          <div>Inactive subscription plans</div>
          <div className="font-semibold text-neutral-900">
            {counts.inactiveSubscriptionPlansCount}
          </div>
        </div>
      </div>
    </SectionCard>
  )
}

function RecentUsersCard({ users }: { users: AdminUser[] }) {
  const navigate = useNavigate()

  return (
    <SectionCard
      title="Recent users"
      description="Newest created users."
      actions={
        <button
          type="button"
          onClick={() => navigate('/admin/users')}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
        >
          View all
        </button>
      }
    >
      <div className="space-y-3">
        {users.map((u) => (
          <div key={u.id} className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="truncate text-sm font-medium text-neutral-900">
                {u.email ?? u.name ?? `User #${u.id}`}
              </div>
              <div className="text-xs text-neutral-500">ID: {u.id}</div>
            </div>
            <div className="shrink-0 text-xs text-neutral-500">{formatDateTime(u.created_at)}</div>
          </div>
        ))}
      </div>
    </SectionCard>
  )
}

function RecentBusinessesCard({ businesses }: { businesses: AdminBusiness[] }) {
  const navigate = useNavigate()

  return (
    <SectionCard
      title="Recent businesses"
      description="Newest created businesses."
      actions={
        <button
          type="button"
          onClick={() => navigate('/admin/businesses')}
          className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
        >
          View all
        </button>
      }
    >
      <div className="space-y-3">
        {businesses.map((b) => (
          <div key={b.id} className="flex items-start justify-between gap-4">
            <div className="min-w-0">
              <div className="truncate text-sm font-medium text-neutral-900">{b.name}</div>
              <div className="text-xs text-neutral-500">ID: {b.id}</div>
            </div>
            <div className="shrink-0 text-xs text-neutral-500">{formatDateTime(b.created_at)}</div>
          </div>
        ))}
      </div>
    </SectionCard>
  )
}

export function AdminDashboardView({ counts, recentUsers, recentBusinesses }: AdminDashboardViewProps) {
  const hasRecentUsers = recentUsers.length > 0
  const hasRecentBusinesses = recentBusinesses.length > 0

  return (
    <div className="space-y-6">
      <header className="space-y-1">
        <h1 className="text-lg font-semibold">Dashboard</h1>
        <p className="text-sm text-neutral-600">
          Overview of users, businesses, moderation and subscription plans.
        </p>
      </header>

      <DashboardGrid className="grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <DashboardStatCard label="Users" value={counts.usersCount} />
        <DashboardStatCard label="Businesses" value={counts.businessesCount} />
        <DashboardStatCard label="Sponsored places" value={counts.sponsoredPlacesCount} />
        <DashboardStatCard label="Pending moderation" value={counts.pendingModerationCount} />
        <DashboardStatCard label="Active plans" value={counts.activeSubscriptionPlansCount} />
      </DashboardGrid>

      <DashboardGrid className="grid-cols-1 md:grid-cols-2">
        <QuickActionsCard />
        <NeedsAttentionCard counts={counts} />
      </DashboardGrid>

      {hasRecentUsers || hasRecentBusinesses ? (
        <DashboardGrid className="grid-cols-1 md:grid-cols-2">
          {hasRecentBusinesses ? <RecentBusinessesCard businesses={recentBusinesses} /> : null}
          {hasRecentUsers ? <RecentUsersCard users={recentUsers} /> : null}
        </DashboardGrid>
      ) : null}
    </div>
  )
}

