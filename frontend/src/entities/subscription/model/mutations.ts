import { useMutation } from '@tanstack/react-query';
import { subscriptionApi } from '../api/subscriptionApi';

export function useMockPurchaseMutation() {
  return useMutation({
    mutationFn: subscriptionApi.mockPurchase,
  });
}

