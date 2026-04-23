import { z } from 'zod'

export const businessMediaFormSchema = z.object({
  type: z.enum(['image', 'logo']),
  url: z.string().trim().min(1, 'URL is required').url('Invalid URL'),
})

