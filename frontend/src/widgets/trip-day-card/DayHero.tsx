import cn from 'classnames';
import { Camera, MapPin, Sparkles } from 'lucide-react';
import type { TripDay } from '../../entities/trip';
import { humanizeToken } from '../../entities/trip/lib/presentation';
import styles from './DayHero.module.scss';

interface DayHeroProps {
  day: TripDay;
}

export function DayHero({ day }: DayHeroProps) {
  const heroImage = day.images?.hero;
  const placeName = day.place_candidate?.name ?? day.location;
  const matchedInterest = humanizeToken(day.place_candidate?.matched_interest);
  const hasHeroImage = Boolean(heroImage?.url);

  return (
    <header
      className={cn(styles.hero, {
        [styles['hero--withImage']]: hasHeroImage,
      })}
    >
      {hasHeroImage && (
        <>
          <img
            src={heroImage?.url}
            alt={heroImage?.alt ?? placeName ?? day.title}
            className={styles.background}
            loading='lazy'
          />
          <div className={styles.overlay} />
        </>
      )}

      <div className={styles.content}>
        <div className={styles.badges}>
          <span className={styles.dayBadge}>Day {day.day}</span>
          <span className={styles.cityBadge}>{day.city}</span>
          {matchedInterest && (
            <span className={styles.cityBadge}>
              <Sparkles size={14} />
              {matchedInterest}
            </span>
          )}
        </div>

        <div className={styles.copy}>
          <p className={styles.placeName}>{placeName}</p>
          <h3 className={styles.title}>{day.title}</h3>
          <p className={styles.location}>
            <MapPin size={16} />
            <span>
              {day.city}
              {day.location && day.location !== day.city ? ` • ${day.location}` : ''}
            </span>
          </p>
        </div>

        {heroImage?.photographer && (
          <p className={styles.credit}>
            <Camera size={14} />
            {heroImage.photographer_url ? (
              <a
                href={heroImage.photographer_url}
                target='_blank'
                rel='noreferrer'
              >
                Photo by {heroImage.photographer}
              </a>
            ) : (
              <span>Photo by {heroImage.photographer}</span>
            )}
          </p>
        )}
      </div>
    </header>
  );
}
