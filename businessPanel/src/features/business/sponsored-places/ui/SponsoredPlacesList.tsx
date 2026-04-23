import type { SponsoredPlace } from '../model/sponsoredPlaces.types'
import { SponsoredPlaceCard } from './SponsoredPlaceCard'

type SponsoredPlacesListProps = {
  places: SponsoredPlace[]
  onEdit: (place: SponsoredPlace) => void
  onDeactivate: (id: number) => void
  deactivatingId?: number | null
}

export function SponsoredPlacesList({
  places,
  onEdit,
  onDeactivate,
  deactivatingId,
}: SponsoredPlacesListProps) {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {places.map((place) => (
        <SponsoredPlaceCard
          key={place.id}
          place={place}
          onEdit={onEdit}
          onDeactivate={onDeactivate}
          isDeactivating={deactivatingId === place.id}
        />
      ))}
    </div>
  )
}

