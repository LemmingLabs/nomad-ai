import axios from 'axios';
import { apiClient } from '../../../shared/api';
import type { CurrentSubscription, SubscriptionPlan } from '../model/types';

export const subscriptionApi = {
  /** GET /subscriptions/plans */
  getPlans: () =>
    apiClient.get<SubscriptionPlan[]>('/subscriptions/plans').then((response) => response.data),

  /** GET /subscriptions/me */
  getMySubscription: async (): Promise<CurrentSubscription | null> => {
    try {
      const response = await apiClient.get<CurrentSubscription>('/subscriptions/me');
      return response.data;
    } catch (error: unknown) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  },

  /** POST /subscriptions/mock-purchase */
  mockPurchase: (payload: { plan_id: number }) =>
    apiClient.post<unknown>('/subscriptions/mock-purchase', payload).then((response) => response.data),
};
