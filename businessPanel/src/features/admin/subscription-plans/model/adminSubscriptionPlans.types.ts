export type BillingPeriod = 'free' | 'monthly' | 'yearly'

export type SubscriptionPlan = {
  id: number
  name: string
  price: number
  currency: string
  billing_period: BillingPeriod
  trip_limit_per_day: number
  chat_edit_limit_per_day: number
  is_active: boolean
}

export type CreateSubscriptionPlanPayload = Omit<SubscriptionPlan, 'id'>

export type UpdateSubscriptionPlanPayload = Partial<CreateSubscriptionPlanPayload>

export type SubscriptionPlanFormValues = {
  name: string
  price: number
  currency: string
  billing_period: BillingPeriod
  trip_limit_per_day: number
  chat_edit_limit_per_day: number
  is_active: boolean
}

