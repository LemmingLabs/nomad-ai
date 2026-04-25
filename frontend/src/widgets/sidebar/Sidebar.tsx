import { useMutation } from '@tanstack/react-query';
import {
  LayoutPanelLeft,
  LayoutPanelTop,
  Plus,
  UserRound,
} from 'lucide-react';
import cn from 'classnames';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import styles from './Sidebar.module.scss';
import { useTripStore } from '../../entities/trip';
import { useUserStore } from '../../entities/user';
import { LogoutButton } from '../../features/auth/logout';
import { deleteTripApi } from '../../features/trip/delete-trip';
import { useSidebarStore } from '../../features/ui/open-sidebar';
import { config } from '../../shared/config';
import { Avatar } from '../../shared/ui';
import { SidebarTripItem } from './SidebarTripItem';
import { UsageWidget } from '../usage-widget';

interface SidebarProps {
  isOpen?: boolean;
  onNewTrip?: () => void;
}

export function Sidebar({ isOpen = true, onNewTrip }: SidebarProps) {
  const navigate = useNavigate();
  const { trips, activeTripId, setActiveTrip, removeTrip } = useTripStore();
  const { isAuthenticated, user } = useUserStore();
  const { isCollapsed, toggleCollapsed } = useSidebarStore();

  const deleteMutation = useMutation({
    mutationFn: async (tripId: number) => {
      if (isAuthenticated) {
        await deleteTripApi.remove(tripId);
      }
      return tripId;
    },
    onSuccess: (tripId) => {
      removeTrip(tripId);
      if (localStorage.getItem(config.storageKeys.guestTripId) === String(tripId)) {
        localStorage.removeItem(config.storageKeys.guestTripId);
      }
      if (activeTripId === tripId) {
        void navigate('/');
      }
      toast.success('Trip removed');
    },
    onError: () => {
      toast.error('Could not delete this trip');
    },
  });

  const startNewTrip = () => {
    if (onNewTrip) {
      onNewTrip();
      return;
    }
    void navigate('/');
  };

  return (
    <aside
      className={cn(styles.sidebar, {
        [styles['sidebar--closed']]: !isOpen,
        [styles['sidebar--collapsed']]: isCollapsed,
      })}
    >
      <div className={styles.header}>
        <button type="button" className={styles.brand} onClick={() => void navigate('/')}>
          <span className={styles.brandMark}>N</span>
          {!isCollapsed && <span className={styles.logo}>NomadAI</span>}
        </button>

        <div className={styles.headerActions}>
          <button
            type="button"
            className={styles.iconButton}
            onClick={startNewTrip}
            aria-label="Create new trip"
            title="Create new trip"
          >
            <Plus size={16} />
          </button>
          <button
            type="button"
            className={styles.iconButton}
            onClick={toggleCollapsed}
            aria-label={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <LayoutPanelTop size={16} /> : <LayoutPanelLeft size={16} />}
          </button>
        </div>
      </div>

      <div className={styles.tripList}>
        {trips.length === 0 && (
          <p className={styles.emptyState}>
            No trips yet. Start a new one!
          </p>
        )}
        {trips.map((trip) => (
          <SidebarTripItem
            key={trip.id}
            trip={trip}
            isActive={activeTripId === trip.id}
            isCollapsed={isCollapsed}
            isDeleting={deleteMutation.isPending}
            onSelect={(tripId) => {
              setActiveTrip(tripId);
              void navigate(`/trip/${tripId}`);
            }}
            onDelete={(tripId) => {
              if (!deleteMutation.isPending) {
                deleteMutation.mutate(tripId);
              }
            }}
          />
        ))}
      </div>

      <UsageWidget isCollapsed={isCollapsed} />

      <div className={styles.footer}>
        {user ? (
          <div className={styles.footerStack}>
            {!isCollapsed && (
              <div className={styles.profileSummary}>
                <Avatar name={user.full_name ?? user.email} size="sm" />
                <div className={styles.profileCopy}>
                  <p className={styles.profileName}>{user.full_name ?? 'Traveler'}</p>
                  <p className={styles.profileEmail}>{user.email}</p>
                </div>
              </div>
            )}
            <LogoutButton isCollapsed={isCollapsed} />
          </div>
        ) : (
          <button
            type="button"
            className={styles.profileButton}
            onClick={() => void navigate('/auth/login')}
            aria-label="Sign in"
          >
            <div className={styles.profile}>
              <span className={styles.profileGhost}>
                <UserRound size={16} />
              </span>
              {!isCollapsed && (
                <div className={styles.profileCopy}>
                  <p className={styles.profileName}>Guest mode</p>
                  <p className={styles.profileEmail}>Sign in to sync your trips</p>
                </div>
              )}
            </div>
          </button>
        )}
      </div>
    </aside>
  );
}
