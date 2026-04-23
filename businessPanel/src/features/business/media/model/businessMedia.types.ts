export type BusinessMediaType = 'image' | 'logo'

export type BusinessMedia = {
  id: number
  business_id: number
  type: BusinessMediaType
  url: string
  created_at?: string
}

export type CreateBusinessMediaPayload = {
  type: BusinessMediaType
  url: string
}

export type BusinessMediaFormValues = {
  type: BusinessMediaType
  url: string
}

