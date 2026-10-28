import cn from 'classnames';
import { MoreHorizontal, Pencil, Trash2 } from 'lucide-react';
import { type FormEvent, useState } from 'react';
import type { TripListItem } from '../../entities/trip';
import styles from './SidebarTripItem.module.scss';

interface SidebarTripItemProps {
  trip: TripListItem;
  isActive: boolean;
  isCollapsed: boolean;
  onSelect: (tripId: number) => void;
  onDelete: (tripId: number) => void;
  onRename: (tripId: number, title: string) => void;
  canRename?: boolean;
  isDeleting?: boolean;
  isSavingRename?: boolean;
}

export function SidebarTripItem({
  trip,
  isActive,
  isCollapsed,
  onSelect,
  onDelete,
  onRename,
  canRename = false,
  isDeleting = false,
  isSavingRename = false,
}: SidebarTripItemProps) {
  const [isConfirmingDelete, setIsConfirmingDelete] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isRenaming, setIsRenaming] = useState(false);
  const [draftTitle, setDraftTitle] = useState(trip.title);
  const [renameError, setRenameError] = useState('');

  const submitRename = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const title = draftTitle.trim();
    if (!title) {
      setRenameError('Enter a trip name.');
      return;
    }
    onRename(trip.id, title);
    setIsRenaming(false);
    setRenameError('');
  };

  return (
    <div
      className={cn(styles.item, {
        [styles['item--active']]: isActive,
        [styles['item--collapsed']]: isCollapsed,
      })}
    >
      <button
        type='button'
        className={styles.main}
        onClick={() => onSelect(trip.id)}
        title={trip.title}
      >
        <span className={styles.marker}>{trip.days}</span>
        <div className={styles.copy}>
          <span className={styles.title}>{trip.title}</span>
          {trip.destination_name && (
            <span className={styles.destination}>{trip.destination_name}</span>
          )}
          <span className={styles.preview}>
            {trip.last_message_preview ?? 'No messages yet'}
          </span>
        </div>
      </button>

      {!isCollapsed && !isConfirmingDelete && !isRenaming && (
        <button
          type='button'
          className={styles.action}
          onClick={() => setIsMenuOpen((open) => !open)}
          aria-label={`Actions for ${trip.title}`}
          aria-expanded={isMenuOpen}
          aria-controls={`trip-actions-${trip.id}`}
        >
          <MoreHorizontal size={16} />
        </button>
      )}

      {!isCollapsed && isMenuOpen && (
        <div
          id={`trip-actions-${trip.id}`}
          className={styles.menu}
          role="group"
          aria-label={`${trip.title} actions`}
        >
          {canRename && (
            <button
              type="button"
              className={styles.menuButton}
              onClick={() => {
                setDraftTitle(trip.title);
                setRenameError('');
                setIsMenuOpen(false);
                setIsRenaming(true);
              }}
            >
              <Pencil size={14} />
              Rename
            </button>
          )}
          <button
            type="button"
            className={cn(styles.menuButton, styles['menuButton--danger'])}
            onClick={() => {
              setIsMenuOpen(false);
              setIsConfirmingDelete(true);
            }}
          >
            <Trash2 size={14} />
            Delete
          </button>
        </div>
      )}

      {!isCollapsed && isRenaming && (
        <form className={styles.renameForm} onSubmit={submitRename}>
          <label className={styles.renameLabel} htmlFor={`trip-title-${trip.id}`}>
            Trip name
          </label>
          <input
            id={`trip-title-${trip.id}`}
            className={styles.renameInput}
            value={draftTitle}
            onChange={(event) => {
              setDraftTitle(event.target.value);
              setRenameError('');
            }}
            maxLength={255}
            aria-invalid={Boolean(renameError)}
            aria-describedby={renameError ? `trip-title-error-${trip.id}` : undefined}
            disabled={isSavingRename}
            autoFocus
          />
          {renameError && (
            <p id={`trip-title-error-${trip.id}`} className={styles.renameError}>
              {renameError}
            </p>
          )}
          <div className={styles.confirmActions}>
            <button
              type="button"
              className={styles.confirmButton}
              onClick={() => setIsRenaming(false)}
              disabled={isSavingRename}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={styles.confirmButton}
              disabled={isSavingRename || draftTitle.length > 255}
            >
              {isSavingRename ? 'Saving…' : 'Save'}
            </button>
          </div>
        </form>
      )}

      {!isCollapsed && isConfirmingDelete && (
        <div className={styles.confirm}>
          <p className={styles.confirmText}>Delete this trip?</p>
          <div className={styles.confirmActions}>
            <button
              type='button'
              className={styles.confirmButton}
              onClick={() => setIsConfirmingDelete(false)}
            >
              Cancel
            </button>
            <button
              type='button'
              className={cn(
                styles.confirmButton,
                styles['confirmButton--danger'],
              )}
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
