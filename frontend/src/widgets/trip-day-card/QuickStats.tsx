import { Clock3, MapPinned, Star, Wallet } from 'lucide-react';
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

  const estimatedHours = Math.max(day.activities.length * 2, 4);
  const stats: StatItem[] = [
    {
      icon: Clock3,
      label: 'Day pace',
      value: `~${estimatedHours}h exploring`,
    },
  ];

  if (day.route_from_previous?.distance_km) {
    stats.push({
      icon: MapPinned,
      label: 'Distance',
      value: `${formatNumber(day.route_from_previous.distance_km)} km`,
    });
  }

  if (day.route_from_previous?.estimated_cost != null) {
    stats.push({
      icon: Wallet,
      label: 'Move cost',
      value: `~${formatNumber(day.route_from_previous.estimated_cost)} KGS`,
    });
  }

  if (rating) {
    stats.push({
      icon: Star,
      label: 'Top rating',
      value: rating.toFixed(1),
    });
  }

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
