import cn from 'classnames';
import { Camera, MapPin, Sparkles } from 'lucide-react';
import { useState } from 'react';
import type { TripDay } from '../../entities/trip';
import { humanizeToken } from '../../entities/trip/lib/presentation';
import styles from './DayHero.module.scss';

interface DayHeroProps {
  day: TripDay;
}

export function DayHero({ day }: DayHeroProps) {
  const heroImage = day.images?.hero;
  const [failedUrl, setFailedUrl] = useState<string | null>(null);
  const placeName = day.place_candidate?.name ?? day.location;
  const matchedInterest = humanizeToken(day.place_candidate?.matched_interest);
  const imageUrl = typeof heroImage?.url === 'string' ? heroImage.url.trim() : '';
  const hasHeroImage = Boolean(imageUrl && imageUrl !== failedUrl);
  const source = typeof heroImage?.source === 'string' ? heroImage.source.trim() : '';
  const photoId = typeof heroImage?.photo_id === 'string' ? heroImage.photo_id : '';
  const pexelsPhotoUrl = source.toLowerCase() === 'pexels' && /^\d+$/.test(photoId)
    ? `https://www.pexels.com/photo/${photoId}/`
    : null;

  return (
    <header
      className={cn(styles.hero, {
        [styles['hero--withImage']]: hasHeroImage,
      })}
    >
      {hasHeroImage && (
        <>
          <img
            src={imageUrl}
            alt={heroImage?.alt?.trim() || 'Travel inspiration photo; exact location not verified'}
            className={styles.background}
            loading='lazy'
            onError={() => setFailedUrl(imageUrl)}
            onLoad={() => setFailedUrl(null)}
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
          <h3 className={styles.title} id={`trip-day-title-${day.day}`}>
            {day.title}
          </h3>
          <p className={styles.location}>
            <MapPin size={16} />
            <span>
              {day.city}
              {day.location && day.location !== day.city ? ` • ${day.location}` : ''}
            </span>
          </p>
        </div>

        {hasHeroImage && (
          <p className={styles.credit}>
            <Camera size={14} aria-hidden='true' />
            <span>Inspiration photo · location not verified</span>
            {heroImage?.photographer && heroImage.photographer_url ? (
              <a
                href={heroImage.photographer_url}
                target='_blank'
                rel='noreferrer'
              >
                Photo by {heroImage.photographer}
              </a>
            ) : heroImage?.photographer ? <span>Photo by {heroImage.photographer}</span> : null}
            {pexelsPhotoUrl ? <a href={pexelsPhotoUrl} target='_blank' rel='noreferrer'>Pexels</a>
              : source ? <span>{source.toLowerCase() === 'pexels' ? 'Pexels' : source}</span> : null}
          </p>
        )}
      </div>
    </header>
  );
}
