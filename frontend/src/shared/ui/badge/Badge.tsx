import cn from 'classnames';
import styles from './Badge.module.scss';

type BadgeVariant = 'accent' | 'success' | 'error' | 'warning' | 'neutral';

interface BadgeProps {
  variant?: BadgeVariant;
  children: React.ReactNode;
  className?: string;
}

export function Badge({ variant = 'neutral', children, className }: BadgeProps) {
  return (
    <span className={cn(styles.badge, styles[`badge--${variant}`], className)}>
      {children}
    </span>
  );
}
