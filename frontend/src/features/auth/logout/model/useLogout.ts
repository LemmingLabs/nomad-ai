import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useTripStore } from '../../../../entities/trip';
import { useUserStore } from '../../../../entities/user';
import { config } from '../../../../shared/config';

export function useLogout() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const clearUser = useUserStore((state) => state.clearUser);
  const clearTrips = useTripStore((state) => state.clearTrips);

  return useMutation({
    mutationFn: async () => {
      await queryClient.cancelQueries();
      window.localStorage.removeItem(config.storageKeys.accessToken);
      clearUser();
      clearTrips();
      queryClient.clear();
    },
    onSuccess: () => {
      toast.success('You have been logged out');
      void navigate('/auth/login', { replace: true });
    },
  });
}
