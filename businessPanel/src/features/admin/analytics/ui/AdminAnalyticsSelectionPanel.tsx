import type { AdminBusiness } from '../../businesses/model/adminBusinesses.types'
import type { AdminSponsoredPlace } from '../../sponsored-moderation/model/adminSponsoredModeration.types'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'

type AdminAnalyticsSelectionPanelProps =
  | {
      mode: 'business'
      items: AdminBusiness[]
      selectedId: number | null
      onSelect: (id: number) => void
    }
  | {
      mode: 'sponsoredPlace'
      items: AdminSponsoredPlace[]
      selectedId: number | null
      onSelect: (id: number) => void
    }

export function AdminAnalyticsSelectionPanel(props: AdminAnalyticsSelectionPanelProps) {
  const { selectedId, onSelect } = props

  return (
    <section className="rounded-lg border border-neutral-200 bg-white p-4">
      <div className="text-sm font-semibold text-neutral-900">
        {props.mode === 'business' ? 'Businesses' : 'Sponsored places'}
      </div>
      <div className="mt-3 space-y-2">
        {props.items.map((item) => {
          const isSelected = selectedId === item.id

          if (props.mode === 'business') {
            const b = item as AdminBusiness
            return (
              <button
                key={b.id}
                type="button"
                onClick={() => onSelect(b.id)}
                className={[
                  'w-full rounded-md border px-3 py-2 text-left',
                  isSelected
                    ? 'border-neutral-900 bg-neutral-50'
                    : 'border-neutral-200 bg-white hover:bg-neutral-50',
                ].join(' ')}
              >
                <div className="truncate text-sm font-medium text-neutral-900">
                  {b.name}
                </div>
                <div className="mt-1 text-xs text-neutral-600">
                  <StatusBadge variant={b.is_active ? 'success' : 'neutral'}>
                    {b.is_active ? 'Active' : 'Inactive'}
                  </StatusBadge>
                </div>
              </button>
            )
          }

          const p = item as AdminSponsoredPlace
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => onSelect(p.id)}
              className={[
                'w-full rounded-md border px-3 py-2 text-left',
                isSelected
                  ? 'border-neutral-900 bg-neutral-50'
                  : 'border-neutral-200 bg-white hover:bg-neutral-50',
              ].join(' ')}
            >
              <div className="truncate text-sm font-medium text-neutral-900">{p.title}</div>
              <div className="mt-1 text-xs text-neutral-600">
                {p.city} • {p.category}
              </div>
              <div className="mt-2 flex flex-wrap gap-2">
                <StatusBadge variant={p.is_approved ? 'success' : 'warning'}>
                  {p.is_approved ? 'Approved' : 'Pending'}
                </StatusBadge>
                <StatusBadge variant={p.is_active ? 'success' : 'neutral'}>
                  {p.is_active ? 'Active' : 'Inactive'}
                </StatusBadge>
              </div>
            </button>
          )
        })}
      </div>
    </section>
  )
}
