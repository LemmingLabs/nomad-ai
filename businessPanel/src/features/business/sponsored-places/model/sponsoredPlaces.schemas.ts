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
  .max(50)
  .refine((value) => value === '' || (/^[+\d\s().-]+$/.test(value) && (value.match(/\d/g)?.length ?? 0) >= 5), {
    message: 'Enter a phone number using the format your team answers',
  })

const locationNumberString = () =>
  z
    .string()
    .trim()
    .refine((value) => value !== '' && Number.isFinite(Number(value)), {
      message: 'Please select a location on the map',
    })

export const sponsoredPlaceFormSchema = z.object({
  country_code: z.string().length(2),
  region: z.string().trim(),
  operating_language: z.string().trim().min(2).max(12),
  title: z.string().trim().min(1, 'Title is required'),
  description: z.string().trim().min(1, 'Description is required'),
  city: z.string().trim().min(1, 'City is required'),
  category: z.string().trim().min(1, 'Category is required'),
  address: z.string().trim().min(1, 'Address is required'),
  lat: locationNumberString(),
  lng: locationNumberString(),
  contact_phone: emptyOrPhone,
  website_url: emptyOrUrl,
  cta_text: z.string().trim(),
})
