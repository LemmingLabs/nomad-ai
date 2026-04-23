import { Link } from 'react-router-dom';
import { useMyLimitsQuery } from '../../entities/limit';
import { useMySubscriptionQuery } from '../../entities/subscription';
import { fallbackFreeLimits, getUsageTone } from '../../features/subscription/view-usage';
import { Button, Skeleton } from '../../shared/ui';
import { UsageProgress } from '../usage-widget';
import styles from './SubscriptionSummary.module.scss';
import { SubscriptionStatusCard } from './SubscriptionStatusCard';

export function SubscriptionSummary() {
  const subscriptionQuery = useMySubscriptionQuery();
  const limitsQuery = useMyLimitsQuery();

  const subscription = subscriptionQuery.data;
  const limits = limitsQuery.data ?? fallbackFreeLimits;
  const status = (subscription?.status ?? 'active').toLowerCase();
  const planName = limits.plan ?? subscription?.plan?.name ?? 'FREE';

  const isLoading = subscriptionQuery.isLoading || limitsQuery.isLoading;

  return (
    <div className={styles.wrap}>
      {isLoading ? (
        <div className={styles.card}>
          <div className={styles.cardInner}>
            <Skeleton height="140px" />
          </div>
        </div>
      ) : (
        <SubscriptionStatusCard
          planName={planName}
          status={status}
          billingPeriod={subscription?.plan?.billing_period ?? null}
          startedAt={subscription?.started_at ?? null}
          expiresAt={subscription?.expires_at ?? null}
        />
      )}

      <div className={styles.card}>
        <div className={styles.cardInner}>
          <div className={styles.titleRow}>
            <h3 className={styles.title}>Usage today</h3>
          </div>

          {limitsQuery.isLoading ? (
            <>
              <Skeleton height="54px" />
              <Skeleton height="54px" />
            </>
          ) : (
            <div className={styles.stack}>
              <UsageProgress
                label="Trips today"
                used={limits.trip_generations_used}
                limit={limits.trip_limit_per_day}
                tone={getUsageTone(limits.trip_generations_used, limits.trip_limit_per_day)}
              />
              <UsageProgress
                label="Chat edits"
                used={limits.chat_edits_used}
                limit={limits.chat_edit_limit_per_day}
                tone={getUsageTone(limits.chat_edits_used, limits.chat_edit_limit_per_day)}
              />
            </div>
          )}

          <div className={styles.actions}>
            <Link to="/pricing">
              <Button type="button" variant="secondary" size="sm">
                View plans
              </Button>
            </Link>
            <Link to="/">
              <Button type="button" variant="ghost" size="sm">
                Back to app
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
