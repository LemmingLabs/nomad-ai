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

  const mockUnavailableForDestination = itinerary.generation_status?.reasons?.includes(
    'mock_unavailable_for_destination',
  ) ?? false;

  return (
    <div id="trip-print-root" className={styles.preview}>
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
        {mockUnavailableForDestination ? (
          <p className={styles.degradedNotice} role="status">
            Development fallback is unavailable for {destinationName ?? 'this destination'}. AI generation was unavailable, so no itinerary was created.
          </p>
        ) : itinerary.generation_status?.state === 'degraded' ? (
          <p className={styles.degradedNotice} role="status">
            This is a draft because AI or route data was unavailable. Review the warnings and confirm logistics before relying on it.
          </p>
        ) : null}
        {itinerary.days.length > 0 ? (
          <p className={styles.suggestionNotice}>
            Activities, timing, and practical notes are suggestions. Durations are estimates when shown; unknown values are left open. Source-reviewed facts and sponsored placements are labeled separately.
          </p>
        ) : null}
        {itinerary.quality_warnings?.map((warning, index) => (
          <p className={styles.warning} key={`${warning.code}-${warning.day ?? index}`}>
            {warning.message}
          </p>
        ))}
        {itinerary.route_status === 'unavailable' ? (
          <p className={styles.warning}>Route details could not be refreshed for this itinerary.</p>
        ) : null}
      </div>
      {itinerary.days.length > 0 ? (
        <div data-print-hide="true">
          <OffersSearchPanel
            countryCode={destinationCountryCode}
            destinationCity={itinerary.days[0]?.city ?? ''}
          />
        </div>
      ) : null}
      {itinerary.days.length > 1 && (
        <nav className={styles.dayNavigation} aria-label="Jump to itinerary day" data-print-hide="true">
          <span className={styles.dayNavigationLabel}>Jump to day</span>
          <ol className={styles.dayNavigationList}>
            {itinerary.days.map((day) => (
              <li key={day.day}>
                <a
                  className={styles.dayNavigationLink}
                  href={`#trip-day-${day.day}`}
                  aria-label={`Day ${day.day}: ${day.title}, ${day.city}`}
                >
                  <span>Day {day.day}</span>
                  <span>{day.city}</span>
                </a>
              </li>
            ))}
          </ol>
        </nav>
      )}
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
