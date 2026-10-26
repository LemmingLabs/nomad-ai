import { z } from 'zod'

const internationalPhoneRegex = /^\+\d{1,3}(?:\s\d{2,4}){1,4}$/

const emptyOrUrl = z
  .string()
  .trim()
  .refine((value) => value === '' || z.string().url().safeParse(value).success, {
    message: 'Invalid URL',
  })

const emptyOrPhone = z
  .string()
  .trim()
  .refine((value) => value === '' || internationalPhoneRegex.test(value), {
    message: 'Enter a phone number with the selected country calling code',
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
