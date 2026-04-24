import { z } from 'zod'

const kyrgyzPhoneRegex = /^\+996\s\d{3}\s\d{3}\s\d{3}$/

const emptyOrUrl = z
  .string()
  .trim()
  .refine((value) => value === '' || z.string().url().safeParse(value).success, {
    message: 'Invalid URL',
  })

const emptyOrPhone = z
  .string()
  .trim()
  .refine((value) => value === '' || kyrgyzPhoneRegex.test(value), {
    message: 'Phone must be in format +996 XXX XXX XXX',
  })

const locationNumberString = () =>
  z
    .string()
    .trim()
    .refine((value) => value !== '' && Number.isFinite(Number(value)), {
      message: 'Please select a location on the map',
    })

export const sponsoredPlaceFormSchema = z.object({
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
