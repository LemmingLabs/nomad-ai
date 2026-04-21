import cn from 'classnames';
import styles from './Divider.module.scss';

interface DividerProps {
  label?: string;
  className?: string;
}

export function Divider({ label, className }: DividerProps) {
  return (
    <div className={cn(styles.divider, className)}>
      {label && <span className={styles.label}>{label}</span>}
    </div>
  );
}
