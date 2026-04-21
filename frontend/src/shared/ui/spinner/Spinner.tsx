import cn from 'classnames';
import styles from './Spinner.module.scss';

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <span className={cn(styles.spinner, styles[`spinner--${size}`], className)} aria-label="Loading" role="status">
      <span className={styles.inner} />
    </span>
  );
}
