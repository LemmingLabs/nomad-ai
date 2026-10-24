import { useQuery } from '@tanstack/react-query';
import { destinationApi } from '../api/destinationApi';
import { destinationQueryKeys } from './queryKeys';

export function useDestinationsQuery() {
  return useQuery({
    queryKey: destinationQueryKeys.all,
    queryFn: destinationApi.listSupported,
    staleTime: 5 * 60 * 1000,
    retry: false,
  });
}
