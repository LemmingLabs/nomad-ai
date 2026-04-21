import cn from 'classnames';
import styles from './Avatar.module.scss';

interface AvatarProps {
  src?: string | null;
  name?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

function getInitials(name?: string): string {
  if (!name) return '?';
  return name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();
}

export function Avatar({ src, name, size = 'md', className }: AvatarProps) {
  return (
    <span className={cn(styles.avatar, styles[`avatar--${size}`], className)}>
      {src
        ? <img src={src} alt={name ?? 'avatar'} className={styles.img} />
        : <span className={styles.initials}>{getInitials(name)}</span>
      }
    </span>
  );
}
