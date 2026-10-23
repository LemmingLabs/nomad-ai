export type SubscriptionBillingPeriod = string;

export type SubscriptionStatus = string;

export interface SubscriptionPlan {
  id: number;
  name: string;
  price: number;
  billing_period: SubscriptionBillingPeriod;
  trip_limit_per_day: number;
  chat_edit_limit_per_day: number;
}

export interface CurrentSubscriptionPlanInfo {
  name: string;
  price: number;
  billing_period: SubscriptionBillingPeriod;
}

export interface CurrentSubscription {
  plan?: CurrentSubscriptionPlanInfo | null;
  status: SubscriptionStatus;
  started_at: string;
  expires_at: string | null;
}
