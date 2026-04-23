import { ArrowUpRight, Globe, MapPin, Phone, Sparkles, Store } from 'lucide-react';
import type { TripDay } from '../../entities/trip';
import { Badge } from '../../shared/ui';
import styles from './SponsoredPlaceCard.module.scss';

interface SponsoredPlaceCardProps {
  day: TripDay;
}

function getPhoneHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, '')}`;
}

function getHostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return 'Website';
  }
}

function getPrimaryHref(day: TripDay): string | null {
  const place = day.sponsored?.place;

  if (!place) {
    return null;
  }

  if (place.website) {
    return place.website;
  }

  if (place.contact) {
    return getPhoneHref(place.contact);
  }

  const query = [place.title, place.address ?? day.location, day.city]
    .filter(Boolean)
    .join(', ');

  return query
    ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`
    : null;
}

export function SponsoredPlaceCard({ day }: SponsoredPlaceCardProps) {
  const sponsored = day.sponsored;

  if (!sponsored?.is_sponsored || !sponsored.place) {
    return null;
  }

  const { place } = sponsored;
  const badgeLabel = sponsored.badge?.trim() || 'Partner Pick';
  const imageUrl = place.images?.[0] ?? null;
  const primaryHref = getPrimaryHref(day);
  const primaryTarget = place.website ? '_blank' : undefined;
  const primaryRel = place.website ? 'noreferrer' : undefined;

  return (
    <section className={styles.card} aria-label='Sponsored partner recommendation'>
      <div className={styles.header}>
        <div className={styles.headerCopy}>
          <div className={styles.badges}>
            <Badge variant='accent' className={styles.badge}>
              {badgeLabel}
            </Badge>
            <span className={styles.kicker}>Sponsored recommendation</span>
          </div>
          <h4 className={styles.heading}>Partner pick for this day</h4>
          <p className={styles.subheading}>
            A curated partner stop that fits this part of the itinerary.
          </p>
        </div>
      </div>

      <div className={styles.content}>
        <div className={styles.media}>
          {imageUrl ? (
            <img
              src={imageUrl}
              alt={place.title}
              className={styles.image}
              loading='lazy'
            />
          ) : (
            <div className={styles.placeholder} aria-hidden='true'>
              <Sparkles size={20} />
              <span>Partner venue</span>
            </div>
          )}
        </div>

        <div className={styles.details}>
          <div className={styles.titleBlock}>
            <h5 className={styles.title}>{place.title}</h5>
            {place.category && (
              <p className={styles.metaRow}>
                <Store size={15} />
                <span>{place.category}</span>
              </p>
            )}
            {place.address && (
              <p className={styles.metaRow}>
                <MapPin size={15} />
                <span>{place.address}</span>
              </p>
            )}
          </div>

          <p className={styles.description}>{place.description}</p>

          <div className={styles.actions}>
            {primaryHref && (
              <a
                href={primaryHref}
                target={primaryTarget}
                rel={primaryRel}
                className={styles.primaryAction}
              >
                <span>{place.cta}</span>
                <ArrowUpRight size={16} />
              </a>
            )}

            {place.website && (
              <a
                href={place.website}
                target='_blank'
                rel='noreferrer'
                className={styles.secondaryAction}
                aria-label={`Open ${place.title} website`}
                title={getHostname(place.website)}
              >
                <Globe size={16} />
                <span>Website</span>
              </a>
            )}

            {place.contact && (
              <a
                href={getPhoneHref(place.contact)}
                className={styles.secondaryAction}
                aria-label={`Call ${place.title}`}
              >
                <Phone size={16} />
                <span>Call</span>
              </a>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
