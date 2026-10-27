export type FlightOfferSearchRequest = {
  kind: 'flight'
  destination_country_code: string
  origin: string
  destination: string
  departure_date: string
  return_date?: string | null
  passengers: number
}

export type StayOfferSearchRequest = {
  kind: 'stay'
  destination_country_code: string
  destination_city: string
  check_in: string
  check_out: string
  adults: number
  rooms: number
}

export type OfferSearchRequest = FlightOfferSearchRequest | StayOfferSearchRequest

export type OffersUnavailableResponse = {
  state: 'unavailable'
  reason:
    | 'feature_disabled'
    | 'provider_unconfigured'
    | 'unsupported_market'
    | 'provider_timeout'
    | 'provider_quota_exceeded'
    | 'provider_error'
    | 'stale_result'
  message: string
}

export type NormalizedOffer = {
  id: string
  kind: 'flight' | 'stay'
  provider: string
  fetched_at: string
  expires_at: string
  currency: string
  total_amount: number | string
  availability: 'available' | 'limited'
  conditions: string[]
  handoff_url: string
}

export type OffersResultsResponse = {
  state: 'results'
  provider: string
  offers: NormalizedOffer[]
}

export type OffersNoResultsResponse = {
  state: 'no_results'
  provider: string
  fetched_at: string
}

export type OfferDemoItem = {
  id: string
  kind: 'flight' | 'stay'
  title: string
  source: 'NomadAI demo fixture'
  example_total: number
  currency: 'USD'
  conditions: string
  handoff_url: null
}

export type OffersDemoResponse = {
  state: 'demo'
  message: string
  offers: OfferDemoItem[]
}

export type OffersSearchResponse =
  | OffersUnavailableResponse
  | OffersDemoResponse
  | OffersResultsResponse
  | OffersNoResultsResponse
