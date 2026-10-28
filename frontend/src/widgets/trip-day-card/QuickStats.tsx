import { MapPinned, Star } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { TripDay } from '../../entities/trip';
import styles from './QuickStats.module.scss';

interface QuickStatsProps {
  day: TripDay;
}

interface StatItem {
  icon: LucideIcon;
  label: string;
  value: string;
}

function formatNumber(value: number): string {
  return new Intl.NumberFormat('en-US', {
    maximumFractionDigits: value >= 10 ? 0 : 1,
  }).format(value);
}

export function QuickStats({ day }: QuickStatsProps) {
  const ratingCandidates = [
    day.hotel?.rating,
    ...(day.recommended_places ?? []).map((place) => place.rating),
  ].filter((rating): rating is number => typeof rating === 'number');

  const rating =
    ratingCandidates.length > 0 ? Math.max(...ratingCandidates) : undefined;

  const stats: StatItem[] = [];

  if (day.route_from_previous?.distance_km) {
    stats.push({
      icon: MapPinned,
      label: 'Distance',
      value: `${formatNumber(day.route_from_previous.distance_km)} km`,
    });
  }

  if (rating) {
    stats.push({
      icon: Star,
      label: 'Top rating',
      value: rating.toFixed(1),
    });
  }

  if (stats.length === 0) return null;

  return (
    <section className={styles.stats} aria-label="Day quick stats">
      {stats.map((stat) => {
        const Icon = stat.icon;

        return (
          <div key={stat.label} className={styles.item}>
            <span className={styles.iconWrap}>
              <Icon size={16} />
            </span>
            <div className={styles.copy}>
              <span className={styles.label}>{stat.label}</span>
              <span className={styles.value}>{stat.value}</span>
            </div>
          </div>
        );
      })}
    </section>
  );
}
