import { Sparkles } from 'lucide-react';
import cn from 'classnames';
import styles from './TripLimitNotice.module.scss';
import type { UsageTone } from '../../lib/usage';

interface TripLimitNoticeProps {
  remaining: number;
  limit: number;
  tone: UsageTone;
}

export function TripLimitNotice({ remaining, limit, tone }: TripLimitNoticeProps) {
  if (!Number.isFinite(limit) || limit <= 0) {
    return (
      <div className={cn(styles.notice, styles.danger)}>
        <div className={styles.copy}>
          <span className={styles.title}>Trip generation is not available on your plan</span>
          <span className={styles.subtitle}>Upgrade to start generating trips with AI.</span>
        </div>
        <Sparkles size={18} />
      </div>
    );
  }

  const title =
    remaining <= 0
      ? "You've reached your daily trip generation limit"
      : remaining <= 2
        ? `Only ${remaining} trip ${remaining === 1 ? 'generation' : 'generations'} left today`
        : `You have ${remaining} trip generations left today`;

  return (
    <div
      className={cn(styles.notice, {
        [styles.warn]: tone === 'warn',
        [styles.danger]: tone === 'danger',
      })}
    >
      <div className={styles.copy}>
        <span className={styles.title}>{title}</span>
        <span className={styles.subtitle}>
          {limit} per day on your current plan.
        </span>
      </div>
      <Sparkles size={18} />
    </div>
  );
}

