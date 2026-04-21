import { Landmark, MapPin, Star, UtensilsCrossed } from 'lucide-react';
import type { TripPlace } from '../../entities/trip';
import styles from './PlaceCard.module.scss';

interface PlaceCardProps {
  place: TripPlace;
}

function getTypeLabel(type: string): string {
  return type.replace(/_/g, ' ');
}

function isFoodType(type: string): boolean {
  return type === 'restaurant' || type === 'cafe';
}

export function PlaceCard({ place }: PlaceCardProps) {
  return (
    <article className={styles.card}>
      <div className={styles.media}>
        {place.image_url ? (
          <img
            src={place.image_url}
            alt={place.name}
            className={styles.image}
            loading="lazy"
          />
        ) : (
          <div className={styles.placeholder}>
            {isFoodType(place.type) ? <UtensilsCrossed size={24} /> : <Landmark size={24} />}
          </div>
        )}
        <span className={styles.type}>{getTypeLabel(place.type)}</span>
      </div>

      <div className={styles.content}>
        <div className={styles.topRow}>
          <h5 className={styles.name}>{place.name}</h5>
          {place.rating != null && (
            <span className={styles.rating}>
              <Star size={14} />
              {place.rating.toFixed(1)}
            </span>
          )}
        </div>

        <p className={styles.city}>{place.city}</p>

        {place.address && (
          <p className={styles.address}>
            <MapPin size={14} />
            <span>{place.address}</span>
          </p>
        )}
      </div>
    </article>
  );
}
