import { Link } from 'react-router-dom';
import { useUserStore } from '../../entities/user';
import { useMyLimitsQuery } from '../../entities/limit';
import { PlanBadge, useMySubscriptionQuery } from '../../entities/subscription';
import {
  fallbackFreeLimits,
  getRemaining,
  getUsageTone,
} from '../../features/subscription/view-usage';
import { Button, Skeleton } from '../../shared/ui';
import { UsageProgress } from './UsageProgress';
import styles from './UsageWidget.module.scss';

interface UsageWidgetProps {
  isCollapsed?: boolean;
}

export function UsageWidget({ isCollapsed = false }: UsageWidgetProps) {
  const { isAuthenticated } = useUserStore();
  const subscriptionQuery = useMySubscriptionQuery();
  const limitsQuery = useMyLimitsQuery();

  const limits = limitsQuery.data ?? (isAuthenticated ? fallbackFreeLimits : null);
  const planName =
    limits?.plan ??
    subscriptionQuery.data?.plan?.name ??
    'FREE';

  if (isCollapsed) {
    return (
      <div className={`${styles.wrap} ${styles.collapsed}`}>
        <PlanBadge planName={planName} />
      </div>
    );
  }

  const isLoading = subscriptionQuery.isLoading || limitsQuery.isLoading;

  return (
    <div className={styles.wrap}>
      <div className={styles.header}>
        <span className={styles.title}>Usage today</span>
        <PlanBadge planName={planName} />
      </div>

      {!isAuthenticated && (
        <>
          <p className={styles.hint}>
            Sign in to track your daily limits and upgrade when you need more generations.
          </p>
          <div className={styles.actions}>
            <Link to="/auth/login">
              <Button type="button" size="sm" variant="secondary">
                Sign in
              </Button>
            </Link>
            <Link to="/pricing">
              <Button type="button" size="sm">
                View plans
              </Button>
            </Link>
          </div>
        </>
      )}

      {isAuthenticated && (
        <div className={styles.stack}>
          {isLoading && (
            <>
              <Skeleton height="54px" />
              <Skeleton height="54px" />
            </>
          )}

          {!isLoading && limits && (
            <>
              <UsageProgress
                label="Trips"
                used={limits.trip_generations_used}
                limit={limits.trip_limit_per_day}
                tone={getUsageTone(limits.trip_generations_used, limits.trip_limit_per_day)}
              />
              <UsageProgress
                label="AI edits"
                used={limits.chat_edits_used}
                limit={limits.chat_edit_limit_per_day}
                tone={getUsageTone(limits.chat_edits_used, limits.chat_edit_limit_per_day)}
              />
              <p className={styles.hint}>
                {getRemaining(limits.trip_generations_used, limits.trip_limit_per_day)} trip generations left.
              </p>
              <div className={styles.actions}>
                <Link to="/pricing">
                  <Button type="button" size="sm" variant="secondary">
                    Upgrade
                  </Button>
                </Link>
                <Link to="/profile">
                  <Button type="button" size="sm" variant="ghost">
                    Details
                  </Button>
                </Link>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
