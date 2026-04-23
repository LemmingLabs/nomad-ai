import { z } from 'zod'

const emptyOrUrl = z
  .string()
  .trim()
  .refine((value) => value === '' || z.string().url().safeParse(value).success, {
    message: 'Invalid URL',
  })

const emptyOrPhone = z
  .string()
  .trim()
  .refine((value) => value === '' || (value.length >= 6 && value.length <= 32), {
    message: 'Invalid phone number',
  })

export const businessProfileFormSchema = z.object({
  name: z.string().trim().min(1, 'Name is required'),
  description: z.string().trim(),
  contact_phone: emptyOrPhone,
  website_url: emptyOrUrl,
})

