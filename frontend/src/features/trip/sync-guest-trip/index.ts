// sync-guest-trip: post a locally stored guest trip after user registers/logs in
import { apiClient } from '../../../shared/api';
import type { Trip } from '../../../entities/trip';

interface SyncGuestTripPayload {
  trip_id: number;
}

export const syncGuestTripApi = {
  sync: (payload: SyncGuestTripPayload) =>
    apiClient.post<Trip>('/trips/sync-guest', payload).then((response) => response.data),
};
