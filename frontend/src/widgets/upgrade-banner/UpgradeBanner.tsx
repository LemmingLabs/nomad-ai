import { Link } from 'react-router-dom';
import { ArrowRight } from 'lucide-react';
import { Button } from '../../shared/ui';
import styles from './UpgradeBanner.module.scss';

interface UpgradeBannerProps {
  title: string;
  subtitle: string;
  ctaTo?: string;
  ctaLabel?: string;
}

export function UpgradeBanner({
  title,
  subtitle,
  ctaTo = '/pricing',
  ctaLabel = 'Upgrade',
}: UpgradeBannerProps) {
  return (
    <div className={styles.banner}>
      <div className={styles.copy}>
        <span className={styles.title}>{title}</span>
        <span className={styles.subtitle}>{subtitle}</span>
      </div>
      <div className={styles.actions}>
        <Link to={ctaTo}>
          <Button type="button" size="sm" rightIcon={<ArrowRight size={16} />}>
            {ctaLabel}
          </Button>
        </Link>
      </div>
    </div>
  );
}

