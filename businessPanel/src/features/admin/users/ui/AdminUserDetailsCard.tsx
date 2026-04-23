import type { AdminUserDetails, UserRole } from '../model/adminUsers.types'
import { formatDateTime } from '../../../../shared/lib/formatDateTime'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'
import { SectionCard } from '../../../../shared/ui/SectionCard'

function roleVariant(role: UserRole) {
  if (role === 'admin') return 'success' as const
  if (role === 'business') return 'warning' as const
  return 'neutral' as const
}

function roleLabel(role: UserRole) {
  if (role === 'admin') return 'Admin'
  if (role === 'business') return 'Business'
  return 'User'
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-start justify-between gap-4">
      <div className="text-sm text-neutral-600">{label}</div>
      <div className="text-sm text-neutral-900">{value}</div>
    </div>
  )
}

type AdminUserDetailsCardProps = {
  user: AdminUserDetails
}

export function AdminUserDetailsCard({ user }: AdminUserDetailsCardProps) {
  return (
    <SectionCard
      title={user.email ? user.email : `User #${user.id}`}
      description="Manage user role and access level."
      actions={
        <StatusBadge variant={roleVariant(user.role)}>{roleLabel(user.role)}</StatusBadge>
      }
    >
      <div className="space-y-3">
        <Row label="User ID" value={String(user.id)} />
        <Row label="Email" value={user.email ?? '—'} />
        <Row label="Role" value={roleLabel(user.role)} />
        <Row label="Created" value={formatDateTime(user.created_at)} />
        <Row label="Updated" value={formatDateTime(user.updated_at)} />
      </div>

      <div className="mt-6 rounded-md border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700">
        <div className="font-medium text-neutral-900">Notes</div>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Assigning <span className="font-medium">business</span> enables business dashboard access.</li>
          <li>Assigning <span className="font-medium">business</span> does not auto-create a business profile.</li>
          <li>Admins cannot change their own role (backend enforced).</li>
          <li>The last remaining admin cannot be downgraded (backend enforced).</li>
        </ul>
      </div>
    </SectionCard>
  )
}

