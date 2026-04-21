import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { LoginForm } from '../../../widgets/auth-form';
import { loginApi, type LoginFormData } from '../../../features/auth/login-by-email';
import { syncGuestTripApi } from '../../../features/trip/sync-guest-trip';
import { useTripStore } from '../../../entities/trip';
import { userApi, useUserStore } from '../../../entities/user';
import { config } from '../../../shared/config';
import { handleApiError } from '../../../shared/lib';
import styles from './AuthPage.module.scss';

export function LoginPage() {
  const navigate = useNavigate();
  const { setUser } = useUserStore();
  const { addTrip, setActiveTrip } = useTripStore();

  const mutation = useMutation({
    mutationFn: loginApi.login,
    onSuccess: async (data) => {
      localStorage.setItem(config.storageKeys.accessToken, data.access_token);
      const user = await userApi.getMe();
      setUser(user);
      const guestTripId = localStorage.getItem(config.storageKeys.guestTripId);

      if (guestTripId) {
        const syncedTrip = await syncGuestTripApi.sync({ trip_id: Number(guestTripId) });
        addTrip(syncedTrip);
        setActiveTrip(syncedTrip.id);
        localStorage.removeItem(config.storageKeys.guestTripId);
        toast.success('Welcome back! Your guest trip is ready.');
        void navigate(`/trip/${syncedTrip.id}`);
        return;
      }

      toast.success('Welcome back!');
      void navigate('/');
    },
    onError: handleApiError,
  });

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>NomadAI</div>
        <LoginForm onSubmit={(data: LoginFormData) => mutation.mutate(data)} isLoading={mutation.isPending} />
      </div>
    </div>
  );
}
