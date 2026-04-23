import { useQuery } from '@tanstack/react-query';
import { subscriptionApi } from '../api/subscriptionApi';
import { subscriptionQueryKeys } from './queryKeys';
import { config } from '../../../shared/config';

function hasAccessToken(): boolean {
  if (typeof window === 'undefined') return false;
  return Boolean(window.localStorage.getItem(config.storageKeys.accessToken));
}

export function useSubscriptionPlansQuery() {
  return useQuery({
    queryKey: subscriptionQueryKeys.plans(),
    queryFn: subscriptionApi.getPlans,
  });
}

export function useMySubscriptionQuery() {
  const enabled = hasAccessToken();

  return useQuery({
    queryKey: subscriptionQueryKeys.me(),
    queryFn: subscriptionApi.getMySubscription,
    enabled,
    retry: false,
  });
}
