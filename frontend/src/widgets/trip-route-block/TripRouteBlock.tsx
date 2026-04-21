import {
  ArrowRight,
  Clock3,
  MapPinned,
  Route,
  Wallet,
} from 'lucide-react';
import type { TripRoute } from '../../entities/trip';
import styles from './TripRouteBlock.module.scss';

interface TripRouteBlockProps {
  route: TripRoute;
}

export function TripRouteBlock({ route }: TripRouteBlockProps) {
  if (
    route.transport_type === 'unknown' ||
    (route.distance_km === 0 && route.duration_mins === 0)
  ) {
    return (
      <section className={styles.block}>
        <div className={styles.header}>
          <span className={styles.iconWrap}>
            <Route size={16} />
          </span>
          <div className={styles.headerCopy}>
            <p className={styles.eyebrow}>Route from previous day</p>
            <h4 className={styles.title}>
              {route.origin} <ArrowRight size={14} /> {route.destination}
            </h4>
          </div>
        </div>
        <p className={styles.fallback}>Route info unavailable for this leg of the trip.</p>
      </section>
    );
  }

  return (
    <section className={styles.block}>
      <div className={styles.header}>
        <span className={styles.iconWrap}>
          <Route size={16} />
        </span>
        <div className={styles.headerCopy}>
          <p className={styles.eyebrow}>Route from previous day</p>
          <h4 className={styles.title}>
            {route.origin} <ArrowRight size={14} /> {route.destination}
          </h4>
        </div>
      </div>

      <div className={styles.stats}>
        <span className={styles.stat}>
          <MapPinned size={14} />
          {route.distance_km} km
        </span>
        <span className={styles.stat}>
          <Clock3 size={14} />
          {route.duration_mins} min
        </span>
        {route.estimated_cost != null && (
          <span className={styles.stat}>
            <Wallet size={14} />
            ~{route.estimated_cost} KGS
          </span>
        )}
      </div>
    </section>
  );
}
