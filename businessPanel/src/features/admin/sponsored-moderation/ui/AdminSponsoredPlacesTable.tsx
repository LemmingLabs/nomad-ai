import type { AdminSponsoredPlace } from '../model/adminSponsoredModeration.types'
import { formatDateTime } from '../../../../shared/lib/formatDateTime'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'

type AdminSponsoredPlacesTableProps = {
  places: AdminSponsoredPlace[]
  selectedPlaceId: number | null
  onSelect: (placeId: number) => void
}

export function AdminSponsoredPlacesTable({
  places,
  selectedPlaceId,
  onSelect,
}: AdminSponsoredPlacesTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-neutral-200 bg-white">
      <table className="min-w-full text-left text-sm">
        <thead className="border-b border-neutral-200 bg-neutral-50 text-xs uppercase tracking-wide text-neutral-500">
          <tr>
            <th className="px-4 py-3">Title</th>
            <th className="px-4 py-3">City</th>
            <th className="px-4 py-3">Category</th>
            <th className="px-4 py-3">Business ID</th>
            <th className="px-4 py-3">Approval</th>
            <th className="px-4 py-3">Active</th>
            <th className="px-4 py-3">Created</th>
            <th className="px-4 py-3 text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          {places.map((p) => {
            const isSelected = selectedPlaceId === p.id
            return (
              <tr
                key={p.id}
                className={[
                  'border-b border-neutral-200 last:border-b-0',
                  isSelected ? 'bg-neutral-50' : 'bg-white',
                ].join(' ')}
              >
                <td className="max-w-[22rem] px-4 py-3">
                  <div className="truncate font-medium text-neutral-900" title={p.title}>
                    {p.title}
                  </div>
                </td>
                <td className="px-4 py-3 text-neutral-700">{p.city}</td>
                <td className="px-4 py-3 text-neutral-700">{p.category}</td>
                <td className="px-4 py-3 text-neutral-700">{p.business_id}</td>
                <td className="px-4 py-3">
                  <StatusBadge variant={p.is_approved ? 'success' : 'warning'}>
                    {p.is_approved ? 'Approved' : 'Pending'}
                  </StatusBadge>
                </td>
                <td className="px-4 py-3">
                  <StatusBadge variant={p.is_active ? 'success' : 'neutral'}>
                    {p.is_active ? 'Active' : 'Inactive'}
                  </StatusBadge>
                </td>
                <td className="px-4 py-3 text-neutral-700">
                  {formatDateTime(p.created_at)}
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    type="button"
                    onClick={() => onSelect(p.id)}
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
