import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '../../shared/ui';
import styles from './LimitReachedModal.module.scss';

interface LimitReachedModalProps {
  open: boolean;
  title: string;
  description: string;
  onClose: () => void;
  primaryCta?: { to: string; label: string };
  secondaryCta?: { to: string; label: string };
}

export function LimitReachedModal({
  open,
  title,
  description,
  onClose,
  primaryCta = { to: '/pricing', label: 'View plans' },
  secondaryCta,
}: LimitReachedModalProps) {
  if (!open || typeof document === 'undefined') return null;

  return createPortal(
    <div
      className={styles.overlay}
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) onClose();
      }}
    >
      <div className={styles.modal}>
        <div className={styles.header}>
          <div>
            <h3 className={styles.title}>{title}</h3>
            <p className={styles.description}>{description}</p>
          </div>
          <button type="button" className={styles.close} onClick={onClose} aria-label="Close">
            <X size={16} />
          </button>
        </div>

        <div className={styles.body}>
          <div className={styles.actions}>
            {secondaryCta && (
              <Link to={secondaryCta.to}>
                <Button type="button" variant="secondary">
                  {secondaryCta.label}
                </Button>
              </Link>
            )}
            <Link to={primaryCta.to} onClick={onClose}>
              <Button type="button">{primaryCta.label}</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}

