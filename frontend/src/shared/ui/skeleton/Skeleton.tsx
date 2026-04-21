import cn from 'classnames';
import styles from './Skeleton.module.scss';

interface SkeletonProps {
  width?: string;
  height?: string;
  rounded?: boolean;
  className?: string;
}

export function Skeleton({ width, height, rounded = false, className }: SkeletonProps) {
  return (
    <span
      className={cn(styles.skeleton, { [styles['skeleton--rounded']]: rounded }, className)}
      style={{ width, height }}
      aria-hidden="true"
    />
  );
}
