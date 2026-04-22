import { ArrowUpRight, Globe, MapPin, Phone, Star } from 'lucide-react';
import type { TripDay } from '../../entities/trip';
import {
  formatCompactNumber,
  getDisplayPlaceTypes,
  humanizeToken,
} from '../../entities/trip/lib/presentation';
import { TagList } from '../../shared/ui';
import styles from './PlaceCandidateCard.module.scss';

interface PlaceCandidateCardProps {
  day: TripDay;
}

function getHostname(url: string): string {
  try {
    return new URL(url).hostname.replace(/^www\./, '');
  } catch {
    return 'Website';
  }
}

function getMapsUrl(
  googleMapsUri?: string | null,
  lat?: number | null,
  lng?: number | null,
): string | null {
  if (googleMapsUri) {
    return googleMapsUri;
  }

  if (lat == null || lng == null) {
    return null;
  }

  return `https://www.google.com/maps/search/?api=1&query=${lat},${lng}`;
}

function getPhoneHref(phone: string): string {
  return `tel:${phone.replace(/[^\d+]/g, '')}`;
}

function formatStatus(status?: string | null): string | null {
  switch (status) {
    case 'OPERATIONAL':
      return 'Open';
    case 'CLOSED_TEMPORARILY':
      return 'Temporarily closed';
    case 'CLOSED_PERMANENTLY':
      return 'Permanently closed';
    default:
      return null;
  }
}

export function PlaceCandidateCard({ day }: PlaceCandidateCardProps) {
  const placeCandidate = day.place_candidate;

  if (!placeCandidate?.name) {
    return (
      <section className={styles.card}>
        <div className={styles.header}>
          <div>
            <h4 className={styles.title}>{day.location}</h4>
          </div>
        </div>

        <p className={styles.fallback}>
          This day is structured as a curated stop around {day.location}.
        </p>
      </section>
    );
  }

  const status = formatStatus(placeCandidate.business_status);
  const types = getDisplayPlaceTypes(placeCandidate.types);
  const matchedInterest = humanizeToken(placeCandidate.matched_interest);
  const mapsUrl = getMapsUrl(
    placeCandidate.google_maps_uri,
    placeCandidate.lat,
    placeCandidate.lng,
  );

  return (
    <section className={styles.card}>
      <div className={styles.header}>
        <div>
          <h4 className={styles.title}>{placeCandidate.name}</h4>
        </div>
        {status && <span className={styles.status}>{status}</span>}
      </div>

      {matchedInterest && (
        <p className={styles.match}>
          Perfect for <strong>{matchedInterest}</strong>
        </p>
      )}

      {placeCandidate.formatted_address && (
        <p className={styles.infoRow}>
          <MapPin size={16} />
          <span>{placeCandidate.formatted_address}</span>
        </p>
      )}

      {(typeof placeCandidate.rating === 'number' ||
        placeCandidate.user_rating_count) && (
        <div className={styles.ratingRow}>
          {typeof placeCandidate.rating === 'number' && (
            <span className={styles.metric}>
              <Star size={14} />
              {placeCandidate.rating.toFixed(1)}
            </span>
          )}
          {placeCandidate.user_rating_count ? (
            <span className={styles.metricMuted}>
              {formatCompactNumber(placeCandidate.user_rating_count)} reviews
            </span>
          ) : null}
        </div>
      )}

      <TagList items={types} tone='accent' />

      <div className={styles.meta}>
        {placeCandidate.international_phone_number && (
          <a
            href={getPhoneHref(placeCandidate.international_phone_number)}
            className={styles.linkRow}
          >
            <Phone size={16} />
            <span>{placeCandidate.international_phone_number}</span>
          </a>
        )}

        {placeCandidate.website_uri && (
          <a
            href={placeCandidate.website_uri}
            target='_blank'
            rel='noreferrer'
            className={styles.linkRow}
          >
            <Globe size={16} />
            <span>{getHostname(placeCandidate.website_uri)}</span>
          </a>
        )}
      </div>

      <div className={styles.actions}>
        {mapsUrl && (
          <a
            href={mapsUrl}
            target='_blank'
            rel='noreferrer'
            className={styles.primaryAction}
          >
            Open in Google Maps
            <ArrowUpRight size={16} />
          </a>
        )}
        {placeCandidate.website_uri && (
          <a
            href={placeCandidate.website_uri}
            target='_blank'
            rel='noreferrer'
            className={styles.secondaryAction}
          >
            Visit website
          </a>
        )}
      </div>
    </section>
  );
}
