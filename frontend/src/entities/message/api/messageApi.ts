import { apiClient } from '../../../shared/api';
import type {
  MessageListResponse,
  SendMessagePayload,
  SendMessageResponse,
} from '../model/types';

export const messageApi = {
  /** GET /trips/:tripId/messages */
  getByTrip: (tripId: number) =>
    apiClient
      .get<MessageListResponse>(`/trips/${tripId}/messages`)
      .then((response) => response.data),

  /** POST /trips/:tripId/messages */
  send: (tripId: number, payload: SendMessagePayload) =>
    apiClient
      .post<SendMessageResponse>(`/trips/${tripId}/messages`, payload)
      .then((response) => response.data),
};
