import type {
  BillingPeriod,
  CreateSubscriptionPlanPayload,
  SubscriptionPlan,
  SubscriptionPlanFormValues,
  UpdateSubscriptionPlanPayload,
} from './adminSubscriptionPlans.types'

export function formatBillingPeriodLabel(period: BillingPeriod) {
  if (period === 'free') return 'Free'
  if (period === 'monthly') return 'Monthly'
  return 'Yearly'
}

export function formatPrice(price: number, currency: string) {
  if (!Number.isFinite(price)) return `— ${currency}`
  const fixed = Math.round(price * 100) / 100
  return `${fixed.toFixed(2)} ${currency}`
}

export function mapPlanToFormValues(plan: SubscriptionPlan): SubscriptionPlanFormValues {
  return {
    name: plan.name,
    price: plan.price,
    currency: plan.currency,
    billing_period: plan.billing_period,
    trip_limit_per_day: plan.trip_limit_per_day,
    chat_edit_limit_per_day: plan.chat_edit_limit_per_day,
    is_active: plan.is_active,
  }
}

export function mapFormValuesToCreatePayload(
  values: SubscriptionPlanFormValues,
): CreateSubscriptionPlanPayload {
  return { ...values }
}

export function mapFormValuesToUpdatePayload(
  values: SubscriptionPlanFormValues,
): UpdateSubscriptionPlanPayload {
  return { ...values }
}

