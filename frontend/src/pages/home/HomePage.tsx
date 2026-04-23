import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-toastify';
import { Sidebar } from '../../widgets/sidebar';
import { GenerateTripForm } from '../../widgets/generate-trip-form';
import { useTripStore } from '../../entities/trip';
import { useUserStore } from '../../entities/user';
import { generateTripApi, type GenerateTripFormData } from '../../features/trip/generate-trip';
import { useSidebarStore } from '../../features/ui/open-sidebar';
import { isLimitExceededError } from '../../features/subscription/view-usage';
import { config } from '../../shared/config';
import { useMediaQuery } from '../../shared/hooks';
import { handleApiError } from '../../shared/lib';
import styles from './HomePage.module.scss';
import { LimitReachedModal } from '../../widgets/limit-reached-modal';
import { limitQueryKeys } from '../../entities/limit';

export function HomePage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { isOpen } = useSidebarStore();
  const { addTrip, setActiveTrip } = useTripStore();
  const { isAuthenticated } = useUserStore();
  const isMobile = useMediaQuery('(max-width: 768px)');
  const [showForm, setShowForm] = useState(false);
  const [limitModalOpen, setLimitModalOpen] = useState(false);

  const generateMutation = useMutation({
    mutationFn: generateTripApi.generate,
      onSuccess: (trip) => {
        addTrip(trip);
        setActiveTrip(trip.id);
        if (!isAuthenticated) {
          localStorage.setItem(config.storageKeys.guestTripId, String(trip.id));
        }
        setShowForm(false);
        toast.success('Trip generated!');
        void queryClient.invalidateQueries({ queryKey: limitQueryKeys.me() });
        void navigate(`/trip/${trip.id}`);
      },
    onError: (error) => {
      if (isLimitExceededError(error)) {
        setLimitModalOpen(true);
        return;
      }
      handleApiError(error);
    },
  });

  return (
    <div className={styles.layout}>
      <Sidebar
        isOpen={!isMobile || isOpen}
        onNewTrip={() => setShowForm(true)}
      />

      <main className={styles.main}>
        {showForm ? (
            <div className={styles.formOverlay}>
              <GenerateTripForm
                onSubmit={(data: GenerateTripFormData) =>
                  generateMutation.mutate({
                    ...data,
                    interests: data.interests
                      .split(',')
                      .map((interest) => interest.trim())
                      .filter(Boolean),
                    prompt: data.prompt?.trim() || undefined,
                  })
                }
                isLoading={generateMutation.isPending}
              />
            <button className={styles.cancelBtn} onClick={() => setShowForm(false)}>Cancel</button>
          </div>
        ) : (
          <div className={styles.welcome}>
            <div className={styles.welcomeContent}>
              <h1 className={styles.welcomeTitle}>Plan your next adventure 🌍</h1>
              <p className={styles.welcomeText}>
                Tell the AI where you want to go and it will create a personalized itinerary for you.
              </p>
              <button className={styles.startBtn} onClick={() => setShowForm(true)}>
                Create a trip
              </button>
              {!isAuthenticated && (
                 <p className={styles.authNote}>
                   <Link to="/auth/login" className={styles.authLink}>Sign in</Link> to save your trips
                 </p>
               )}
            </div>
          </div>
        )}
      </main>

      <LimitReachedModal
        open={limitModalOpen}
        title="Daily trip generation limit reached"
        description="Upgrade your plan to generate more trips today and keep iterating on your itinerary."
        onClose={() => setLimitModalOpen(false)}
        primaryCta={{ to: '/pricing', label: 'Upgrade' }}
        secondaryCta={!isAuthenticated ? { to: '/auth/login', label: 'Sign in' } : undefined}
      />
    </div>
  );
}
