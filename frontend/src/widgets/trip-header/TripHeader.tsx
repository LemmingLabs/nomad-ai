import type { ReactNode } from 'react';
import {
  CalendarRange,
  Compass,
  Sparkles,
  Wallet,
} from 'lucide-react';
import { formatTravelStyle } from '../../entities/trip/lib/presentation';
import { TagList } from '../../shared/ui';
import styles from './TripHeader.module.scss';

interface TripHeaderProps {
  title: string;
  totalDays: number;
  summary?: string;
  budget?: string;
  travelStyle?: string;
  interests?: string[];
  actions?: ReactNode;
}

export function TripHeader({
  title,
  totalDays,
  summary,
  budget,
  travelStyle,
  interests,
  actions,
}: TripHeaderProps) {
  const travelStyleLabel = formatTravelStyle(travelStyle);

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

        <div className={styles.stats}>
          <div className={styles.stat}>
            <span className={styles.statIcon}>
              <CalendarRange size={16} />
            </span>
            <div>
              <span className={styles.statLabel}>Trip length</span>
              <strong className={styles.statValue}>{totalDays} days</strong>
            </div>
          </div>

          {budget && (
            <div className={styles.stat}>
              <span className={styles.statIcon}>
                <Wallet size={16} />
              </span>
              <div>
                <span className={styles.statLabel}>Budget</span>
                <strong className={styles.statValue}>{budget}</strong>
              </div>
            </div>
          )}

          {travelStyleLabel && (
            <div className={styles.stat}>
              <span className={styles.statIcon}>
                <Compass size={16} />
              </span>
              <div>
                <span className={styles.statLabel}>Travel style</span>
                <strong className={styles.statValue}>{travelStyleLabel}</strong>
              </div>
            </div>
          )}
        </div>

        <TagList items={interests ?? []} tone='surface' className={styles.tags} />
      </div>
    </header>
  );
}
