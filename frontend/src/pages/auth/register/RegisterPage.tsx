import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { RegisterForm } from '../../../widgets/auth-form';
import { loginApi } from '../../../features/auth/login-by-email';
import { registerApi } from '../../../features/auth/register-by-email';
import type { RegisterFormData } from '../../../features/auth/register-by-email';
import { syncGuestTripApi } from '../../../features/trip/sync-guest-trip';
import { useTripStore } from '../../../entities/trip';
import { userApi, useUserStore } from '../../../entities/user';
import { config } from '../../../shared/config';
import { handleApiError } from '../../../shared/lib';
import styles from './AuthPage.module.scss';

export function RegisterPage() {
  const navigate = useNavigate();
  const { setUser } = useUserStore();
  const { addTrip, setActiveTrip } = useTripStore();

  const mutation = useMutation({
    mutationFn: async (data: RegisterFormData) => {
      await registerApi.register({ email: data.email, password: data.password });
      const loginResponse = await loginApi.login({
        email: data.email,
        password: data.password,
      });
      localStorage.setItem(config.storageKeys.accessToken, loginResponse.access_token);
      return userApi.getMe();
    },
    onSuccess: async (user) => {
      setUser(user);
      const guestTripId = localStorage.getItem(config.storageKeys.guestTripId);

      if (guestTripId) {
        const syncedTrip = await syncGuestTripApi.sync({ trip_id: Number(guestTripId) });
        addTrip(syncedTrip);
        setActiveTrip(syncedTrip.id);
        localStorage.removeItem(config.storageKeys.guestTripId);
        toast.success('Account created! Your guest trip is now synced.');
        void navigate(`/trip/${syncedTrip.id}`);
        return;
      }

      toast.success('Account created! Welcome to NomadAI 🌍');
      void navigate('/');
    },
    onError: handleApiError,
  });

  return (
    <div className={styles.page}>
      <div className={styles.card}>
        <div className={styles.brand}>NomadAI</div>
        <RegisterForm onSubmit={(data) => mutation.mutate(data)} isLoading={mutation.isPending} />
      </div>
    </div>
  );
}
