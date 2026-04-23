import { PlanBadge } from '../../entities/subscription';
import { formatDate } from '../../shared/lib';
import styles from './SubscriptionSummary.module.scss';

interface SubscriptionStatusCardProps {
  planName: string;
  status: string;
  billingPeriod?: string | null;
  startedAt?: string | null;
  expiresAt?: string | null;
}

function normalizeStatus(value: string): string {
  return value.toLowerCase();
}

export function SubscriptionStatusCard({
  planName,
  status,
  billingPeriod,
  startedAt,
  expiresAt,
}: SubscriptionStatusCardProps) {
  const normalized = normalizeStatus(status);

  return (
    <div className={styles.card}>
      <div className={styles.cardInner}>
        <div className={styles.titleRow}>
          <h3 className={styles.title}>Subscription</h3>
          <PlanBadge planName={planName} />
        </div>

        <div className={styles.metaGrid}>
          <div>
            <div className={styles.metaLabel}>Status</div>
            <div className={styles.metaValue}>
              <span className={styles.status} data-status={normalized}>
                <span className={styles.statusDot} aria-hidden="true" />
                {normalized}
              </span>
            </div>
          </div>
          <div>
            <div className={styles.metaLabel}>Billing</div>
            <div className={styles.metaValue}>{billingPeriod ?? '—'}</div>
          </div>
          <div>
            <div className={styles.metaLabel}>Started</div>
            <div className={styles.metaValue}>
              {startedAt ? formatDate(startedAt) : '—'}
            </div>
          </div>
          <div>
            <div className={styles.metaLabel}>Renews / Expires</div>
            <div className={styles.metaValue}>
              {expiresAt ? formatDate(expiresAt) : '—'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

