export type BusinessProfile = {
  id: number
  owner_id?: number
  name: string
  description: string | null
  contact_phone: string | null
  website_url: string | null
  is_active?: boolean
  created_at?: string
  updated_at?: string
}

export type BusinessProfileUpsertPayload = {
  name: string
  description: string | null
  contact_phone: string | null
  website_url: string | null
}

export type BusinessProfileFormValues = {
  name: string
  description: string
  contact_phone: string
  website_url: string
}

