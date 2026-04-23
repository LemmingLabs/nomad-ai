export type AdminSponsoredPlace = {
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
}

export type AdminSponsoredPlaceDetails = AdminSponsoredPlace

export type ModerationAction = 'approve' | 'reject' | 'activate' | 'deactivate'

export type AdminSponsoredPlaceListFilters = {
  preset: 'all' | 'pending' | 'approved' | 'inactive'
}

