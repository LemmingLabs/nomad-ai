import { Check } from 'lucide-react';
import cn from 'classnames';
import type { SubscriptionPlan } from '../../entities/subscription';
import { UpgradeCTA } from '../../features/subscription/upgrade-plan';
import { Button } from '../../shared/ui';
import styles from './PricingPlanCard.module.scss';

function formatBillingPeriod(period: string): string {
  const normalized = period.toLowerCase();
  if (normalized === 'monthly') return '/month';
  if (normalized === 'yearly') return '/year';
  return `/${period}`;
}

function planDescription(planName: string): string {
  const normalized = planName.toUpperCase();
  if (normalized === 'FREE') return 'Start exploring and generate your first itinerary.';
  if (normalized === 'PRO') return 'Best for active planners who refine and iterate with AI.';
  return 'Unlock more daily generations and AI edits.';
}

function formatTripLimit(limit: number): string {
  if (limit <= 0) return 'Trip generation is not included';
  if (limit === 1) return 'Generate up to 1 trip per day';
  return `Generate up to ${limit} trips per day`;
}

function formatChatEditLimit(limit: number): string {
  if (limit <= 0) return 'No AI refinements included';
  if (limit === 1) return 'Refine your trip with AI 1 time a day';
  return `Refine your trip with AI up to ${limit} times a day`;
}

interface PricingPlanCardProps {
  plan: SubscriptionPlan;
  isCurrent: boolean;
  isFeatured?: boolean;
}

export function PricingPlanCard({ plan, isCurrent, isFeatured = false }: PricingPlanCardProps) {
  const isFree = plan.price <= 0;

  return (
    <div className={cn(styles.card, { [styles.featured]: isFeatured })}>
      <div className={styles.top}>
        <div>
          <h3 className={styles.name}>{plan.name}</h3>
          <p className={styles.desc}>{planDescription(plan.name)}</p>
        </div>

        <div className={styles.price} aria-label="Plan price">
          <span className={styles.amount}>{isFree ? '$0' : `$${plan.price}`}</span>
          <span className={styles.period}>{isFree ? 'forever' : formatBillingPeriod(plan.billing_period)}</span>
        </div>
      </div>

      <ul className={styles.list}>
        <li className={styles.item}>
          <Check size={16} className={styles.itemIcon} />
          <span>{formatTripLimit(plan.trip_limit_per_day)}</span>
        </li>
        <li className={styles.item}>
          <Check size={16} className={styles.itemIcon} />
          <span>{formatChatEditLimit(plan.chat_edit_limit_per_day)}</span>
        </li>
        <li className={styles.item}>
          <Check size={16} className={styles.itemIcon} />
          <span>Progress-aware usage UI in sidebar</span>
        </li>
      </ul>

      <div className={styles.cta}>
        {isCurrent ? (
          <Button type="button" variant="secondary" className={styles.current} disabled>
            Current plan
          </Button>
        ) : (
          <UpgradeCTA
            planId={plan.id}
            label={isFree ? 'Choose plan' : 'Upgrade'}
            size="md"
          />
        )}
      </div>

      {!isCurrent && (
        <span className={styles.hint}>
          Mock purchase only — no real billing.
        </span>
      )}
    </div>
  );
}

