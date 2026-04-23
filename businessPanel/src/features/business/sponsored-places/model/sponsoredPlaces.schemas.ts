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

const numberString = (label: string) =>
  z
    .string()
    .trim()
    .refine((value) => value !== '' && Number.isFinite(Number(value)), {
      message: `${label} must be a number`,
    })

export const sponsoredPlaceFormSchema = z.object({
  title: z.string().trim().min(1, 'Title is required'),
  description: z.string().trim().min(1, 'Description is required'),
  city: z.string().trim().min(1, 'City is required'),
  category: z.string().trim().min(1, 'Category is required'),
  address: z.string().trim().min(1, 'Address is required'),
  lat: numberString('Latitude'),
  lng: numberString('Longitude'),
  contact_phone: emptyOrPhone,
  website_url: emptyOrUrl,
  cta_text: z.string().trim(),
})
