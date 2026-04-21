import { apiClient } from '../../../../shared/api';
import type { Trip } from '../../../../entities/trip';

interface GeneratePayload {
  budget: string;
  days: number;
  interests: string[];
  travel_style: string;
  prompt?: string;
}

export const generateTripApi = {
  generate: (payload: GeneratePayload) =>
    apiClient.post<Trip>('/trips/generate', payload).then(r => r.data),
};
