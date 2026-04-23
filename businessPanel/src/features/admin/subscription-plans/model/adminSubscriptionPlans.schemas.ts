import { z } from 'zod'

export const subscriptionPlanFormSchema = z.object({
  name: z.string().trim().min(1, 'Name is required'),
  price: z.number().min(0, 'Price must be >= 0'),
  currency: z.string().trim().min(1, 'Currency is required'),
  billing_period: z.enum(['free', 'monthly', 'yearly']),
  trip_limit_per_day: z.number().int().min(0, 'Trip limit must be >= 0'),
  chat_edit_limit_per_day: z.number().int().min(0, 'Chat edit limit must be >= 0'),
  is_active: z.boolean(),
})

