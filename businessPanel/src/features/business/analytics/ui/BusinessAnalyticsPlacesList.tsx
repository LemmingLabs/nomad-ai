import type { SponsoredPlace } from '../../sponsored-places/model/sponsoredPlaces.types'
import { BusinessAnalyticsPlaceCard } from './BusinessAnalyticsPlaceCard'

type BusinessAnalyticsPlacesListProps = {
  places: SponsoredPlace[]
}

export function BusinessAnalyticsPlacesList({ places }: BusinessAnalyticsPlacesListProps) {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      {places.map((place) => (
        <BusinessAnalyticsPlaceCard key={place.id} place={place} />
      ))}
    </div>
  )
}

