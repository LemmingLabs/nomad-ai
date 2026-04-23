import { Wand2 } from 'lucide-react';
import cn from 'classnames';
import styles from './ChatEditLimitNotice.module.scss';
import type { UsageTone } from '../../lib/usage';

interface ChatEditLimitNoticeProps {
  remaining: number;
  limit: number;
  tone: UsageTone;
}

export function ChatEditLimitNotice({ remaining, limit, tone }: ChatEditLimitNoticeProps) {
  if (!Number.isFinite(limit) || limit <= 0) {
    return (
      <div className={styles.wrap}>
        <span className={cn(styles.badge, styles.danger)}>
          <Wand2 size={14} />
          AI edits not included
        </span>
        <span>Upgrade to refine your trip in chat.</span>
      </div>
    );
  }

  const label =
    remaining <= 0
      ? "You've reached today's AI edit limit"
      : remaining <= 2
        ? `Only ${remaining} edits left today`
        : `${remaining} edits left today`;

  return (
    <div className={styles.wrap}>
      <span
        className={cn(styles.badge, {
          [styles.warn]: tone === 'warn',
          [styles.danger]: tone === 'danger',
        })}
      >
        <Wand2 size={14} />
        {label}
      </span>
      <span>
        {limit} per day on your plan
      </span>
    </div>
  );
}

