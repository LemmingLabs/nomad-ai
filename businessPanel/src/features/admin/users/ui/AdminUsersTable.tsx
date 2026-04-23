import type { AdminUser, UserRole } from '../model/adminUsers.types'
import { formatDateTime } from '../../../../shared/lib/formatDateTime'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'

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

type AdminUsersTableProps = {
  users: AdminUser[]
  selectedUserId: number | null
  onSelect: (userId: number) => void
}

export function AdminUsersTable({ users, selectedUserId, onSelect }: AdminUsersTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-neutral-200 bg-neutral-50 text-xs uppercase tracking-wide text-neutral-500">
          <tr>
            <th className="px-4 py-3">ID</th>
            <th className="px-4 py-3">Email</th>
            <th className="px-4 py-3">Role</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => {
            const isSelected = selectedUserId === u.id
            return (
              <tr
                key={u.id}
                className={[
                  'border-b border-neutral-200 last:border-b-0',
                  isSelected ? 'bg-neutral-50' : 'bg-white',
                ].join(' ')}
              >
                <td className="px-4 py-3 text-neutral-700">{u.id}</td>
                <td className="max-w-[22rem] px-4 py-3">
                  <div className="truncate font-medium text-neutral-900" title={u.email ?? ''}>
                    {u.email ?? '—'}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <StatusBadge variant={roleVariant(u.role)}>{roleLabel(u.role)}</StatusBadge>
                </td>
                <td className="px-4 py-3 text-neutral-700">{formatDateTime(u.created_at)}</td>
                <td className="px-4 py-3 text-right">
                  <button
                    type="button"
                    onClick={() => onSelect(u.id)}
                    className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
                  >
                    View details
                  </button>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

