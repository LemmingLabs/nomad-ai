export type SponsoredPlaceMediaType = 'image' | 'logo' | 'cover'

export type SponsoredPlaceMedia = {
  id: number
  sponsored_place_id?: number
  business_id?: number
  url: string
  type?: SponsoredPlaceMediaType
  filename?: string
  content_type?: string
  created_at?: string
}

export type UploadSponsoredPlaceMediaPayload = {
  placeId: number
  file: File
  type?: SponsoredPlaceMediaType
}

export type DeleteSponsoredPlaceMediaPayload = {
  placeId: number
  mediaId: number
}
