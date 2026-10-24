import { apiClient } from '../../../shared/api';
import type { Destination } from '../model/types';

export const destinationApi = {
  listSupported: async (): Promise<Destination[]> => {
    const response = await apiClient.get<Destination[]>('/destinations');
    return response.data;
  },
};
