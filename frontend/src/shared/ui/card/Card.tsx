import { type HTMLAttributes, type ReactNode } from 'react';
import cn from 'classnames';
import styles from './Card.module.scss';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  padding?: 'sm' | 'md' | 'lg' | 'none';
  hoverable?: boolean;
  children: ReactNode;
}

export function Card({ padding = 'md', hoverable = false, children, className, ...rest }: CardProps) {
  return (
    <div
      className={cn(
        styles.card,
        styles[`card--p-${padding}`],
        { [styles['card--hoverable']]: hoverable },
        className,
      )}
      {...rest}
    >
      {children}
    </div>
  );
}
