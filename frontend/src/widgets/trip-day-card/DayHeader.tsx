import { MapPin, Sparkles } from 'lucide-react';
import type { TripImage } from '../../entities/trip';
import styles from './DayHeader.module.scss';

interface DayHeaderProps {
  dayNumber: number;
  title: string;
  city: string;
  location: string;
  heroImage?: TripImage;
}

export function DayHeader({
  dayNumber,
  title,
  city,
  location,
  heroImage,
}: DayHeaderProps) {
  const hasHero = Boolean(heroImage?.url);

  return (
    <header className={styles.header}>
      {hasHero ? (
        <div className={styles.hero}>
          <img
            src={heroImage?.url}
            alt={heroImage?.alt ?? title}
            className={styles.heroImage}
            loading="lazy"
          />
          <div className={styles.heroShade} />
          <div className={styles.heroContent}>
            <div className={styles.badges}>
              <span className={styles.dayBadge}>Day {dayNumber}</span>
              <span className={styles.cityBadge}>
                <Sparkles size={14} />
                {city}
              </span>
            </div>
            <div className={styles.copy}>
              <h3 className={styles.title}>{title}</h3>
              <p className={styles.location}>
                <MapPin size={16} />
                <span>
                  {city} - {location}
                </span>
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className={styles.content}>
          <div className={styles.badges}>
            <span className={styles.dayBadge}>Day {dayNumber}</span>
            <span className={styles.cityBadge}>{city}</span>
          </div>
          <div className={styles.copy}>
            <h3 className={styles.title}>{title}</h3>
            <p className={styles.location}>
              <MapPin size={16} />
              <span>{location}</span>
            </p>
          </div>
        </div>
      )}
    </header>
  );
}
