export type MessageRole = 'user' | 'assistant';

export interface Message {
  id: number;
  trip_id: number;
  role: MessageRole;
  content: string;
  created_at: string;
}

export interface SendMessagePayload {
  content: string;
}

export interface SendMessageResponse {
  message: Message;
  updated_itinerary: import('../../trip/model/types').TripItinerary | null;
}

export interface MessageListResponse {
  total: number;
  limit: number;
  offset: number;
  items: Message[];
}
