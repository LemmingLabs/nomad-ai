import cn from 'classnames';
import styles from './UsageProgress.module.scss';
import type { UsageTone } from '../../features/subscription/view-usage';
import { getUsageRatio } from '../../features/subscription/view-usage';

interface UsageProgressProps {
  label: string;
  used: number;
  limit: number;
  tone: UsageTone;
}

export function UsageProgress({ label, used, limit, tone }: UsageProgressProps) {
  const ratio = getUsageRatio(used, limit);
  const pct = `${Math.round(ratio * 100)}%`;

  return (
    <div className={styles.row}>
      <div className={styles.top}>
        <span className={styles.label}>{label}</span>
        <span className={styles.meta}>
          {used} / {limit}
        </span>
      </div>
      <div className={styles.bar} aria-label={`${label} usage`}>
        <div
          className={cn(styles.fill, {
            [styles.fillWarn]: tone === 'warn',
            [styles.fillDanger]: tone === 'danger',
          })}
          style={{ width: pct }}
        />
      </div>
    </div>
  );
}

