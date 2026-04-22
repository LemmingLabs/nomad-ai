import cn from 'classnames';
import {
  ArrowRight,
  CarFront,
  Clock3,
  MapPinned,
  Route,
  Wallet,
} from 'lucide-react';
import type { TripRoute } from '../../entities/trip';
import {
  formatDistance,
  formatDuration,
  formatEstimatedCost,
  humanizeToken,
  isRouteAvailable,
} from '../../entities/trip/lib/presentation';
import styles from './RouteTransition.module.scss';

interface RouteTransitionProps {
  route: TripRoute;
}

export function RouteTransition({ route }: RouteTransitionProps) {
  const routeAvailable = isRouteAvailable(route);
  const distance = formatDistance(route.distance_km);
  const duration = formatDuration(route.duration_mins);
  const estimatedCost = formatEstimatedCost(route.estimated_cost);
  const transportType = humanizeToken(route.transport_type);

  return (
    <section
      className={cn(styles.block, {
        [styles['block--fallback']]: !routeAvailable,
      })}
    >
      <div className={styles.rail} aria-hidden='true' />

      <div className={styles.header}>
        <span className={styles.iconWrap}>
          <Route size={16} />
        </span>
        <div className={styles.headerCopy}>
          <p className={styles.eyebrow}>Route transition</p>
          <h4 className={styles.title}>
            {route.origin}
            <ArrowRight size={14} />
            {route.destination}
          </h4>
        </div>
        {transportType && <span className={styles.transport}>{transportType}</span>}
      </div>

      {routeAvailable ? (
        <div className={styles.stats}>
          {distance && (
            <span className={styles.stat}>
              <MapPinned size={14} />
              {distance}
            </span>
          )}
          {duration && (
            <span className={styles.stat}>
              <Clock3 size={14} />
              {duration}
            </span>
          )}
          {estimatedCost && (
            <span className={styles.stat}>
              <Wallet size={14} />
              {estimatedCost}
            </span>
          )}
          {transportType && (
            <span className={styles.stat}>
              <CarFront size={14} />
              {transportType}
            </span>
          )}
        </div>
      ) : (
        <p className={styles.fallback}>
          This leg is part of the journey, but detailed transfer metrics were not
          available from routing.
        </p>
      )}
    </section>
  );
}
