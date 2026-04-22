import {
  BedDouble,
  CarFront,
  Landmark,
  MoonStar,
  MountainSnow,
  ShoppingBag,
  Sparkles,
  SunMedium,
  Sunrise,
  Trees,
  UtensilsCrossed,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { TripActivity } from '../../entities/trip';
import styles from './ActivityTimeline.module.scss';

interface ActivityTimelineProps {
  activities: TripActivity[];
}

function getActivityIcon(type: string): LucideIcon {
  const normalizedType = type.toLowerCase();

  if (normalizedType.includes('food')) return UtensilsCrossed;
  if (normalizedType.includes('nature')) return Trees;
  if (normalizedType.includes('adventure')) return MountainSnow;
  if (normalizedType.includes('rest')) return BedDouble;
  if (normalizedType.includes('shopping')) return ShoppingBag;
  if (normalizedType.includes('transport')) return CarFront;
  if (normalizedType.includes('culture')) return Landmark;

  return Sparkles;
}

function getTimeBucket(time: string): { label: string; icon: LucideIcon } {
  const normalizedTime = time.toLowerCase();

  if (normalizedTime.includes('morning')) {
    return { label: 'Morning', icon: Sunrise };
  }

  if (normalizedTime.includes('afternoon')) {
    return { label: 'Afternoon', icon: SunMedium };
  }

  if (normalizedTime.includes('evening') || normalizedTime.includes('night')) {
    return { label: 'Evening', icon: MoonStar };
  }

  const hour = Number.parseInt(time, 10);

  if (Number.isFinite(hour)) {
    if (hour < 12) {
      return { label: 'Morning', icon: Sunrise };
    }

    if (hour < 17) {
      return { label: 'Afternoon', icon: SunMedium };
    }
  }

  return { label: 'Evening', icon: MoonStar };
}

export function ActivityTimeline({ activities }: ActivityTimelineProps) {
  if (activities.length === 0) {
    return (
      <section className={styles.timelineSection}>
        <div className={styles.sectionHeader}>
          <p className={styles.eyebrow}>Daily rhythm</p>
          <h4 className={styles.title}>Activity timeline</h4>
        </div>

        <div className={styles.emptyState}>
          The AI did not return timed activity blocks for this day yet.
        </div>
      </section>
    );
  }

  return (
    <section className={styles.timelineSection}>
      <div className={styles.sectionHeader}>
        <p className={styles.eyebrow}>Daily rhythm</p>
        <h4 className={styles.title}>Activity timeline</h4>
      </div>

      <ol className={styles.timeline}>
        {activities.map((activity) => {
          const Icon = getActivityIcon(activity.type);
          const timeBucket = getTimeBucket(activity.time);
          const TimeIcon = timeBucket.icon;
          const activityKey = `${activity.time}-${activity.description}`;

          return (
            <li key={activityKey} className={styles.item}>
              <div className={styles.marker}>
                <Icon size={16} />
              </div>
              <div className={styles.card}>
                <div className={styles.meta}>
                  <span className={styles.bucket}>
                    <TimeIcon size={14} />
                    {timeBucket.label}
                  </span>
                  <span className={styles.time}>{activity.time}</span>
                </div>
                <p className={styles.description}>{activity.description}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
