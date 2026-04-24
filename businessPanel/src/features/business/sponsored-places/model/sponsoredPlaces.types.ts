import type { SponsoredPlaceMedia } from '../media/model/sponsoredPlaceMedia.types'

export type SponsoredPlace = {
  id: number
  business_id: number
  title: string
  description: string
  city: string
  lat: number
  lng: number
  category: string
  address: string
  contact_phone: string | null
  website_url: string | null
  cta_text: string | null
  is_active: boolean
  is_approved: boolean
  created_at?: string
  media?: SponsoredPlaceMedia[]
}

export type CreateSponsoredPlacePayload = {
  title: string
  description: string
  city: string
  lat: number
  lng: number
  category: string
  address: string
  contact_phone: string | null
  website_url: string | null
  cta_text: string | null
}

export type UpdateSponsoredPlacePayload = Partial<CreateSponsoredPlacePayload>

export type SponsoredPlaceFormValues = {
  title: string
  description: string
  city: string
  category: string
  address: string
  lat: string
  lng: string
  contact_phone: string
  website_url: string
  cta_text: string
}

export type SponsoredPlaceLocationValue = {
  lat: string
  lng: string
  address: string
  city: string
}
