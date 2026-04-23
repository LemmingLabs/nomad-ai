export interface TripImage {
  source?: string;
  photo_id?: string;
  url: string;
  photographer?: string;
  photographer_url?: string;
  alt?: string;
  search_query?: string;
}

export interface TripImages {
  hero?: TripImage;
  gallery?: TripImage[];
}

export interface TripActivity {
  time: string;
  description: string;
  type: string;
}

export interface TripPlaceCandidate {
  provider?: string;
  place_id?: string;
  name?: string | null;
  city?: string | null;
  formatted_address?: string | null;
  lat?: number | null;
  lng?: number | null;
  rating?: number | null;
  user_rating_count?: number | null;
  types?: string[];
  google_maps_uri?: string | null;
  website_uri?: string | null;
  international_phone_number?: string | null;
  business_status?: string | null;
  matched_interest?: string | null;
  score?: number | null;
}

export interface TripHotel {
  id: number;
  name: string;
  city: string;
  rating?: number | null;
  price_level?: string | null;
  price_from?: number | null;
  address?: string;
  image_url?: string | null;
}

export interface TripPlace {
  id: number;
  name: string;
  city: string;
  rating?: number | null;
  type: string;
  price_level?: string | null;
  address?: string | null;
  image_url?: string | null;
  is_sponsored?: boolean;
  sponsored?: boolean;
}

export interface TripRoute {
  origin: string;
  destination: string;
  distance_km: number;
  duration_mins: number;
  transport_type: string;
  estimated_cost?: number | null;
}

export interface TripDay {
  day: number;
  title: string;
  city: string;
  location: string;
  routing_location?: string;
  activities: TripActivity[];
  hotel?: TripHotel | null;
  recommended_places?: TripPlace[];
  place_candidate?: TripPlaceCandidate | null;
  route_from_previous?: TripRoute | null;
  images?: TripImages | null;
}

export interface TripItinerary {
  summary: string;
  total_days: number;
  interests?: string[];
  travel_style?: string;
  days: TripDay[];
}

export interface TripListItem {
  id: number;
  title: string;
  days: number;
  created_at: string;
  updated_at: string;
  last_message_preview?: string | null;
}

export interface Trip extends TripListItem {
  budget: string;
  interests: string[];
  travel_style: string;
  itinerary_json: TripItinerary;
}

export interface TripDetailResponse {
  trip: Trip;
  messages: {
    total: number;
    limit: number;
    offset: number;
    items: import('../../message').Message[];
  };
}
