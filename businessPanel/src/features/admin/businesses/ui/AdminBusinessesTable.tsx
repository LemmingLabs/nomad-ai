import type { AdminBusiness } from '../model/adminBusinesses.types'
import { formatDateTime } from '../../../../shared/lib/formatDateTime'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'

type AdminBusinessesTableProps = {
  businesses: AdminBusiness[]
  selectedBusinessId: number | null
  onSelect: (businessId: number) => void
}

export function AdminBusinessesTable({
  businesses,
  selectedBusinessId,
  onSelect,
}: AdminBusinessesTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-neutral-200 bg-neutral-50 text-xs uppercase tracking-wide text-neutral-500">
          <tr>
            <th className="px-4 py-3">Name</th>
            <th className="px-4 py-3">Status</th>
            <th className="px-4 py-3">Phone</th>
            <th className="px-4 py-3">Website</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          {businesses.map((b) => {
            const isSelected = selectedBusinessId === b.id
            return (
              <tr
                key={b.id}
                className={[
                  'border-b border-neutral-200 last:border-b-0',
                  isSelected ? 'bg-neutral-50' : 'bg-white',
                ].join(' ')}
              >
                <td className="max-w-[22rem] px-4 py-3">
                  <div className="truncate font-medium text-neutral-900" title={b.name}>
                    {b.name}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <StatusBadge variant={b.is_active ? 'success' : 'neutral'}>
                    {b.is_active ? 'Active' : 'Inactive'}
                  </StatusBadge>
                </td>
                <td className="px-4 py-3 text-neutral-700">{b.contact_phone ?? '—'}</td>
                <td className="max-w-[18rem] px-4 py-3">
                  {b.website_url ? (
                    <a
                      href={b.website_url}
                      target="_blank"
                      rel="noreferrer"
                      className="block truncate underline"
                      title={b.website_url}
                    >
                      {b.website_url}
                    </a>
                  ) : (
                    <span className="text-neutral-700">—</span>
                  )}
                </td>
                <td className="px-4 py-3 text-neutral-700">
                  {formatDateTime(b.created_at)}
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    type="button"
                    onClick={() => onSelect(b.id)}
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
