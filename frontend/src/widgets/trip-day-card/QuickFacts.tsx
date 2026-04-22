import { CarFront, Heart, MapPin, Star, Users } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { TripDay } from '../../entities/trip';
import {
  formatCompactNumber,
  formatDistance,
  formatDuration,
  humanizeToken,
  isRouteAvailable,
} from '../../entities/trip/lib/presentation';
import styles from './QuickFacts.module.scss';

interface QuickFactsProps {
  day: TripDay;
}

interface FactItem {
  icon: LucideIcon;
  label: string;
  value: string;
}

export function QuickFacts({ day }: QuickFactsProps) {
  const placeCandidate = day.place_candidate;
  const routeAvailable = isRouteAvailable(day.route_from_previous);
  const routeDistance = formatDistance(day.route_from_previous?.distance_km);
  const routeDuration = formatDuration(day.route_from_previous?.duration_mins);

  const facts: FactItem[] = [
    {
      icon: MapPin,
      label: 'City',
      value: day.city,
    },
  ];

  if (typeof placeCandidate?.rating === 'number') {
    facts.push({
      icon: Star,
      label: 'Rating',
      value: placeCandidate.rating.toFixed(1),
    });
  }

  if (placeCandidate?.user_rating_count) {
    facts.push({
      icon: Users,
      label: 'Reviews',
      value: formatCompactNumber(placeCandidate.user_rating_count) ?? String(placeCandidate.user_rating_count),
    });
  }

  if (placeCandidate?.matched_interest) {
    facts.push({
      icon: Heart,
      label: 'Best for',
      value: humanizeToken(placeCandidate.matched_interest) ?? placeCandidate.matched_interest,
    });
  }

  if (routeAvailable && (routeDistance || routeDuration)) {
    facts.push({
      icon: CarFront,
      label: 'Transfer',
      value: [routeDistance, routeDuration].filter(Boolean).join(' • '),
    });
  }

  return (
    <section className={styles.row} aria-label='Day quick facts'>
      {facts.map((fact) => {
        const Icon = fact.icon;

        return (
          <div key={fact.label} className={styles.item}>
            <span className={styles.iconWrap}>
              <Icon size={16} />
            </span>
            <div className={styles.copy}>
              <span className={styles.label}>{fact.label}</span>
              <span className={styles.value}>{fact.value}</span>
            </div>
          </div>
        );
      })}
    </section>
  );
}
