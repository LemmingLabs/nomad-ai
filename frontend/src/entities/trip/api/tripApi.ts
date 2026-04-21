import { apiClient } from '../../../shared/api';
import type { TripDetailResponse, TripListItem } from '../model/types';

export const tripApi = {
  /** GET /trips — list all trips for the current user */
  getAll: () =>
    apiClient
      .get<{ items: TripListItem[] }>('/trips')
      .then((response) => response.data.items),

  /** GET /trips/:id — get trip with messages */
  getById: (id: number) =>
    apiClient.get<TripDetailResponse>(`/trips/${id}`).then((response) => response.data),

  /** DELETE /trips/:id */
  remove: (id: number) => apiClient.delete<void>(`/trips/${id}`),
};
