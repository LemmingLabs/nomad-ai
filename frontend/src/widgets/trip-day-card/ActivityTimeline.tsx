import { Compass, MoonStar, SunMedium, Sunrise } from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import type { TripActivity } from '../../entities/trip';
import styles from './ActivityTimeline.module.scss';

interface ActivityTimelineProps {
  activities: TripActivity[];
}

function getActivityIcon(time: string): LucideIcon {
  const normalizedTime = time.toLowerCase();

  if (normalizedTime.includes('morning')) return Sunrise;
  if (normalizedTime.includes('afternoon')) return SunMedium;
  if (normalizedTime.includes('evening')) return MoonStar;

  return Compass;
}

export function ActivityTimeline({ activities }: ActivityTimelineProps) {
  if (activities.length === 0) {
    return null;
  }

  return (
    <section className={styles.timelineSection}>
      <div className={styles.sectionHeader}>
        <p className={styles.eyebrow}>Daily rhythm</p>
        <h4 className={styles.title}>Activity timeline</h4>
      </div>

      <ol className={styles.timeline}>
        {activities.map((activity) => {
          const Icon = getActivityIcon(activity.time);
          const activityKey = `${activity.time}-${activity.description}`;

          return (
            <li key={activityKey} className={styles.item}>
              <div className={styles.marker}>
                <Icon size={16} />
              </div>
              <div className={styles.card}>
                <span className={styles.time}>{activity.time}</span>
                <p className={styles.description}>{activity.description}</p>
              </div>
            </li>
          );
        })}
      </ol>
    </section>
  );
}
