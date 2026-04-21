import type { ReactNode } from 'react';
import { Compass, Sparkles } from 'lucide-react';
import styles from './TripHeader.module.scss';

interface TripHeaderProps {
  title: string;
  totalDays: number;
  summary?: string;
  travelStyle?: string;
  interests?: string[];
  actions?: ReactNode;
}

export function TripHeader({
  title,
  totalDays,
  summary,
  travelStyle,
  interests,
  actions,
}: TripHeaderProps) {
  return (
    <header className={styles.header}>
      <div className={styles.topRow}>
        <div className={styles.eyebrow}>
          <span className={styles.kicker}>
            <Sparkles size={14} />
            AI trip story
          </span>
          <span className={styles.badge}>{totalDays} days</span>
        </div>
        {actions && <div className={styles.actions}>{actions}</div>}
      </div>

      <div className={styles.content}>
        <div className={styles.copy}>
          <h1 className={styles.title}>{title}</h1>
          {summary && <p className={styles.summary}>{summary}</p>}
        </div>

        <div className={styles.meta}>
          {travelStyle && (
            <span className={styles.chip}>
              <Compass size={14} />
              {travelStyle}
            </span>
          )}
          {(interests ?? []).slice(0, 3).map((interest) => (
            <span key={interest} className={styles.chip}>
              {interest}
            </span>
          ))}
        </div>
      </div>
    </header>
  );
}
