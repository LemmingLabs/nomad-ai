import cn from 'classnames';
import styles from './TagList.module.scss';

type TagTone = 'neutral' | 'accent' | 'surface';

interface TagListProps {
  items: string[];
  className?: string;
  tone?: TagTone;
}

export function TagList({
  items,
  className,
  tone = 'neutral',
}: TagListProps) {
  if (items.length === 0) {
    return null;
  }

  return (
    <ul className={cn(styles.list, styles[`list--${tone}`], className)}>
      {items.map((item) => (
        <li key={item} className={styles.item}>
          {item}
        </li>
      ))}
    </ul>
  );
}
