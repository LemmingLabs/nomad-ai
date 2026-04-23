import cn from 'classnames';
import styles from './PlanBadge.module.scss';

interface PlanBadgeProps {
  planName: string;
  className?: string;
}

export function PlanBadge({ planName, className }: PlanBadgeProps) {
  const normalizedPlan = planName?.toUpperCase?.() ? planName.toUpperCase() : planName;

  return (
    <span className={cn(styles.badge, className)} data-plan={normalizedPlan}>
      <span className={styles.dot} aria-hidden="true" />
      {normalizedPlan || 'FREE'}
    </span>
  );
}

