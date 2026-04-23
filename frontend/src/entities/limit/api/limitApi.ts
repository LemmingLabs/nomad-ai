import axios from 'axios';
import { apiClient } from '../../../shared/api';
import type { Limits } from '../model/types';

export const limitApi = {
  /** GET /subscriptions/me/limits */
  getMyLimits: async (): Promise<Limits | null> => {
    try {
      const response = await apiClient.get<Limits>('/subscriptions/me/limits');
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },
};
