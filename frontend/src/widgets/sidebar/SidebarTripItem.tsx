import { useState } from 'react';
import { MoreHorizontal, Trash2 } from 'lucide-react';
import cn from 'classnames';
import type { TripListItem } from '../../entities/trip';
import styles from './SidebarTripItem.module.scss';

interface SidebarTripItemProps {
  trip: TripListItem;
  isActive: boolean;
  isCollapsed: boolean;
  onSelect: (tripId: number) => void;
  onDelete: (tripId: number) => void;
  isDeleting?: boolean;
}

export function SidebarTripItem({
  trip,
  isActive,
  isCollapsed,
  onSelect,
  onDelete,
  isDeleting = false,
}: SidebarTripItemProps) {
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);

  return (
    <div
      className={cn(styles.item, {
        [styles['item--active']]: isActive,
        [styles['item--collapsed']]: isCollapsed,
      })}
    >
      <button
        type="button"
        className={styles.main}
        onClick={() => onSelect(trip.id)}
        title={trip.title}
      >
        <span className={styles.marker}>{trip.days}</span>
        <div className={styles.copy}>
          <span className={styles.title}>{trip.title}</span>
          <span className={styles.preview}>
            {trip.last_message_preview ?? 'No messages yet'}
          </span>
        </div>
      </button>

      {!isCollapsed && !isConfirmingDelete && (
        <button
          type="button"
          className={styles.action}
          onClick={() => setIsConfirmingDelete(true)}
          aria-label={`Delete ${trip.title}`}
        >
          <MoreHorizontal size={16} />
        </button>
      )}

      {!isCollapsed && isConfirmingDelete && (
        <div className={styles.confirm}>
          <p className={styles.confirmText}>Delete this trip?</p>
          <div className={styles.confirmActions}>
            <button
              type="button"
              className={styles.confirmButton}
              onClick={() => setIsConfirmingDelete(false)}
            >
              Cancel
            </button>
            <button
              type="button"
              className={cn(styles.confirmButton, styles['confirmButton--danger'])}
              onClick={() => {
                onDelete(trip.id);
                setIsConfirmingDelete(false);
              }}
              disabled={isDeleting}
            >
              <Trash2 size={14} />
              Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
