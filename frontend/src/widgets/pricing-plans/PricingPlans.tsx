import { useMemo } from 'react';
import { useSubscriptionPlansQuery, useMySubscriptionQuery } from '../../entities/subscription';
import { useMyLimitsQuery } from '../../entities/limit';
import { Skeleton } from '../../shared/ui';
import styles from './PricingPlans.module.scss';
import { PricingPlanCard } from './PricingPlanCard';

export function PricingPlans() {
  const plansQuery = useSubscriptionPlansQuery();
  const subscriptionQuery = useMySubscriptionQuery();
  const limitsQuery = useMyLimitsQuery();

  const currentPlanName =
    limitsQuery.data?.plan ??
    subscriptionQuery.data?.plan?.name ??
    'FREE';

  const plans = useMemo(() => {
    const items = plansQuery.data ?? [];
    return [...items].sort((a, b) => a.price - b.price);
  }, [plansQuery.data]);

  return (
    <div className={styles.wrap}>
      <div className={styles.header}>
        <h2 className={styles.title}>Choose the plan that matches your pace</h2>
        <p className={styles.subtitle}>
          Track your daily usage right inside the product. Upgrade only when you need more
          generations or refinements.
        </p>
      </div>

      {plansQuery.isLoading && (
        <div className={styles.grid}>
          <Skeleton height="280px" />
          <Skeleton height="280px" />
          <Skeleton height="280px" />
        </div>
      )}

      {plansQuery.isSuccess && (
        <div className={styles.grid}>
          {plans.map((plan) => (
            <PricingPlanCard
              key={plan.id}
              plan={plan}
              isCurrent={plan.name.toUpperCase() === currentPlanName.toUpperCase()}
              isFeatured={plan.name.toUpperCase() === 'PRO'}
            />
          ))}
        </div>
      )}
    </div>
  );
}
