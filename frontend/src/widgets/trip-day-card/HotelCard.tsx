import { Building2, MapPin, Star, Wallet } from 'lucide-react';
import type { TripHotel } from '../../entities/trip';
import styles from './HotelCard.module.scss';

interface HotelCardProps {
  hotel: TripHotel;
}

function formatPrice(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: 0,
  }).format(value);
}

export function HotelCard({ hotel }: HotelCardProps) {
  return (
    <section className={styles.section}>
      <div className={styles.sectionHeader}>
        <p className={styles.eyebrow}>Stay</p>
        <h4 className={styles.title}>Where to check in</h4>
      </div>

      <article className={styles.card}>
        <div className={styles.media}>
          {hotel.image_url ? (
            <img
              src={hotel.image_url}
              alt={hotel.name}
              className={styles.image}
              loading="lazy"
            />
          ) : (
            <div className={styles.placeholder}>
              <Building2 size={28} />
            </div>
          )}
          {hotel.rating != null && (
            <span className={styles.rating}>
              <Star size={14} />
              {hotel.rating.toFixed(1)}
            </span>
          )}
        </div>

        <div className={styles.content}>
          <h5 className={styles.name}>{hotel.name}</h5>

          <div className={styles.meta}>
            {hotel.address && (
              <p className={styles.metaItem}>
                <MapPin size={15} />
                <span>{hotel.address}</span>
              </p>
            )}
            {hotel.price_from != null && (
              <p className={styles.metaItem}>
                <Wallet size={15} />
                <span>From {formatPrice(hotel.price_from)} / night</span>
              </p>
            )}
          </div>
        </div>
      </article>
    </section>
  );
}
