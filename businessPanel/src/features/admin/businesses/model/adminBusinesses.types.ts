export type AdminBusiness = {
  id: number
  owner_id: number
  name: string
  description: string | null
  contact_phone: string | null
  website_url: string | null
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export type AdminBusinessDetails = AdminBusiness

