import type { SponsoredPlace } from '../model/sponsoredPlaces.types'
import { StatusBadge } from '../../../../shared/ui/StatusBadge'
import { SponsoredPlaceMediaManager } from '../media/ui/SponsoredPlaceMediaManager'

type SponsoredPlaceCardProps = {
  place: SponsoredPlace
  onEdit: (place: SponsoredPlace) => void
  onDeactivate: (id: number) => void
  isDeactivating?: boolean
}

export function SponsoredPlaceCard({
  place,
  onEdit,
  onDeactivate,
  isDeactivating,
}: SponsoredPlaceCardProps) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <div className="text-sm font-semibold text-neutral-900">{place.title}</div>
          <div className="mt-1 text-sm text-neutral-700">
            {place.city} • {place.category}
          </div>

          <div className="mt-3 flex flex-wrap gap-2">
            <StatusBadge variant={place.is_approved ? 'success' : 'warning'}>
              {place.is_approved ? 'Approved' : 'Pending'}
            </StatusBadge>
            <StatusBadge variant={place.is_active ? 'success' : 'neutral'}>
              {place.is_active ? 'Active' : 'Inactive'}
            </StatusBadge>
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-2">
          <button
            type="button"
            onClick={() => onEdit(place)}
            className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium hover:bg-neutral-50"
          >
            Edit
          </button>
          <button
            type="button"
            onClick={() => onDeactivate(place.id)}
            disabled={isDeactivating || !place.is_active}
            className="rounded-md border border-neutral-200 bg-white px-3 py-1.5 text-sm font-medium text-red-700 hover:bg-neutral-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isDeactivating ? 'Deactivating...' : 'Deactivate'}
          </button>
        </div>
      </div>

      <SponsoredPlaceMediaManager
        placeId={place.id}
        initialItems={place.media ?? []}
      />
    </div>
  )
}
