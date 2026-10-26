import type { ReactNode } from 'react';
import { Fragment } from 'react';
import type { TripItinerary } from '../../entities/trip';
import { TripDayCard } from '../trip-day-card';
import { TripHeader } from '../trip-header';
import { RouteTransition } from '../trip-route-block';
import { OffersSearchPanel } from '../offers-search/OffersSearchPanel';
import styles from './TripPreview.module.scss';

interface TripPreviewProps {
  itinerary: TripItinerary | null | undefined;
  tripId?: number;
  tripTitle?: string;
  destinationName?: string;
  destinationCountryCode?: string;
  budget?: string;
  actions?: ReactNode;
}

export function TripPreview({
  itinerary,
  tripId,
  tripTitle,
  destinationName,
  destinationCountryCode,
  budget,
  actions,
}: TripPreviewProps) {
  if (!itinerary) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyIcon}>🗺️</div>
        <h3>Your itinerary will appear here</h3>
        <p>Chat with the AI to generate your personalized trip plan</p>
      </div>
    );
  }

  return (
    <div className={styles.preview}>
      <TripHeader
        title={tripTitle ?? itinerary.summary ?? 'Your itinerary'}
        destinationName={destinationName}
        totalDays={itinerary.total_days || itinerary.days.length}
        summary={itinerary.summary ?? ''}
        budget={budget}
        travelStyle={itinerary.travel_style}
        interests={itinerary.interests}
        actions={actions}
      />
      <div className={styles.guidance}>
        {itinerary.generation_status?.state === 'degraded' ? (
          <p className={styles.degradedNotice} role="status">
            This is a draft because AI or route data was unavailable. Review the warnings and confirm logistics before relying on it.
          </p>
        ) : null}
        <p className={styles.suggestionNotice}>
          Activities, timing, and practical notes are suggestions. Durations are estimates when shown; unknown values are left open.
        </p>
        {itinerary.quality_warnings?.map((warning, index) => (
          <p className={styles.warning} key={`${warning.code}-${warning.day ?? index}`}>
            {warning.message}
          </p>
        ))}
        {itinerary.route_status === 'unavailable' ? (
          <p className={styles.warning}>Route details could not be refreshed for this itinerary.</p>
        ) : null}
      </div>
      <OffersSearchPanel
        countryCode={destinationCountryCode}
        destinationCity={itinerary.days[0]?.city ?? ''}
      />
      <div className={styles.journey}>
        {itinerary.days.map((day) => (
          <Fragment key={day.day}>
            {day.route_from_previous && (
              <RouteTransition route={day.route_from_previous} />
            )}
            <TripDayCard day={day} tripId={tripId} />
          </Fragment>
        ))}
      </div>
    </div>
  );
}
