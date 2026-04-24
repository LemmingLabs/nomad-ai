import { ArrowUpRight, Globe, MapPin, Phone, Sparkles, Store } from 'lucide-react';
import type { SponsoredPlacePayload } from '../../../entities/trip';
import { resolveAssetUrl } from '../../../shared/lib/resolveAssetUrl';
import { Badge } from '../../../shared/ui';
import { trackSponsoredInteraction } from '../api/sponsoredInteractionsApi';
import styles from './SponsoredCard.module.scss';

interface SponsoredCardProps {
  sponsored: SponsoredPlacePayload;
  tripId?: number | null;
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

function getMapsHref(title: string, address?: string | null): string | null {
  const query = [title, address].filter(Boolean).join(', ');
  return query
    ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(query)}`
    : null;
}

function getPrimaryAction(place: SponsoredPlacePayload['place'], mapsHref: string | null) {
  if (!place?.cta) {
    return null;
  }

  if (place.website) {
    return {
      href: place.website,
      target: '_blank' as const,
      interactionType: 'click' as const,
    };
  }

  if (place.contact) {
    return {
      href: getPhoneHref(place.contact),
      target: '_self' as const,
      interactionType: 'click' as const,
    };
  }

  if (mapsHref) {
    return {
      href: mapsHref,
      target: '_blank' as const,
      interactionType: 'click' as const,
    };
  }

  return null;
}

async function trackAndOpen(
  href: string,
  target: '_blank' | '_self' | undefined,
  sponsoredPlaceId: number,
  businessId: number,
  interactionType: 'click' | 'open_website' | 'open_map' | 'call',
  tripId?: number | null,
) {
  await trackSponsoredInteraction({
    tripId,
    sponsoredPlaceId,
    businessId,
    interactionType,
  });

  if (typeof window === 'undefined') {
    return;
  }

  if (target === '_blank') {
    window.open(href, '_blank', 'noopener,noreferrer');
    return;
  }

  window.location.assign(href);
}

export function SponsoredCard({ sponsored, tripId }: SponsoredCardProps) {
  if (!sponsored?.is_sponsored || !sponsored.place) {
    return null;
  }

  const { place } = sponsored;
  const badgeLabel = sponsored.badge?.trim() || 'Partner Pick';
  const imageUrl = place.images?.[0] ? resolveAssetUrl(place.images[0]) : null;
  const mapsHref = getMapsHref(place.title, place.address);
  const primaryAction = getPrimaryAction(place, mapsHref);

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
            {place.cta && primaryAction && (
              <button
                type='button'
                className={styles.primaryAction}
                onClick={() =>
                  void trackAndOpen(
                    primaryAction.href,
                    primaryAction.target,
                    place.id,
                    place.business_id,
                    primaryAction.interactionType,
                    tripId,
                  )
                }
              >
                <span>{place.cta}</span>
                <ArrowUpRight size={16} />
              </button>
            )}

            {place.website && (
              <button
                type='button'
                className={styles.secondaryAction}
                aria-label={`Open ${place.title} website`}
                title={getHostname(place.website)}
                onClick={() =>
                  void trackAndOpen(
                    place.website!,
                    '_blank',
                    place.id,
                    place.business_id,
                    'open_website',
                    tripId,
                  )
                }
              >
                <Globe size={16} />
                <span>Website</span>
              </button>
            )}

            {place.contact && (
              <button
                type='button'
                className={styles.secondaryAction}
                aria-label={`Call ${place.title}`}
                onClick={() =>
                  void trackAndOpen(
                    getPhoneHref(place.contact!),
                    '_self',
                    place.id,
                    place.business_id,
                    'call',
                    tripId,
                  )
                }
              >
                <Phone size={16} />
                <span>Call</span>
              </button>
            )}

            {mapsHref && (
              <button
                type='button'
                className={styles.secondaryAction}
                onClick={() =>
                  void trackAndOpen(
                    mapsHref,
                    '_blank',
                    place.id,
                    place.business_id,
                    'open_map',
                    tripId,
                  )
                }
              >
                <MapPin size={16} />
                <span>Map</span>
              </button>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
