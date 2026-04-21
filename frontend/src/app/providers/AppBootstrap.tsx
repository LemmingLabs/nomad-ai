import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { tripApi, useTripStore } from '../../entities/trip';
import { userApi, useUserStore } from '../../entities/user';
import { config } from '../../shared/config';

export function AppBootstrap() {
  const { isAuthenticated, setUser, clearUser } = useUserStore();
  const { setTrips } = useTripStore();
  const hasAccessToken =
    typeof window !== 'undefined' &&
    Boolean(window.localStorage.getItem(config.storageKeys.accessToken));

  useEffect(() => {
    if (!hasAccessToken) {
      clearUser();
    }
  }, [clearUser, hasAccessToken]);

  const meQuery = useQuery({
    queryKey: ['auth', 'me'],
    queryFn: userApi.getMe,
    enabled: hasAccessToken,
    retry: false,
  });

  useEffect(() => {
    if (meQuery.data) {
      setUser(meQuery.data);
    }
  }, [meQuery.data, setUser]);

  useEffect(() => {
    if (meQuery.isError && typeof window !== 'undefined') {
      window.localStorage.removeItem(config.storageKeys.accessToken);
      clearUser();
    }
  }, [clearUser, meQuery.isError]);

  const tripsQuery = useQuery({
    queryKey: ['trips'],
    queryFn: tripApi.getAll,
    enabled: hasAccessToken && (isAuthenticated || meQuery.isSuccess),
  });

  useEffect(() => {
    if (tripsQuery.data) {
      setTrips(tripsQuery.data);
    }
  }, [setTrips, tripsQuery.data]);

  return null;
}
