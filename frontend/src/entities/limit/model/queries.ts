import { useQuery } from '@tanstack/react-query';
import { limitApi } from '../api/limitApi';
import { limitQueryKeys } from './queryKeys';
import { config } from '../../../shared/config';

function hasAccessToken(): boolean {
  if (typeof window === 'undefined') return false;
  return Boolean(window.localStorage.getItem(config.storageKeys.accessToken));
}

export function useMyLimitsQuery() {
  const enabled = hasAccessToken();

  return useQuery({
    queryKey: limitQueryKeys.me(),
    queryFn: limitApi.getMyLimits,
    enabled,
    retry: false,
  });
}
