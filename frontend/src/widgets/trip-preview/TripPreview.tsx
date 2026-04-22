import type { ReactNode } from 'react';
import { Fragment } from 'react';
import type { TripItinerary } from '../../entities/trip';
import { TripDayCard } from '../trip-day-card';
import { TripHeader } from '../trip-header';
import { RouteTransition } from '../trip-route-block';
import styles from './TripPreview.module.scss';

interface TripPreviewProps {
  itinerary: TripItinerary | null | undefined;
  tripTitle?: string;
  budget?: string;
  actions?: ReactNode;
}

export function TripPreview({
  itinerary,
  tripTitle,
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
        title={tripTitle ?? itinerary.summary}
        totalDays={itinerary.total_days || itinerary.days.length}
        summary={itinerary.summary}
        budget={budget}
        travelStyle={itinerary.travel_style}
        interests={itinerary.interests}
        actions={actions}
      />
      <div className={styles.journey}>
        {itinerary.days.map((day) => (
          <Fragment key={day.day}>
            {day.route_from_previous && (
              <RouteTransition route={day.route_from_previous} />
            )}
            <TripDayCard day={day} />
          </Fragment>
        ))}
      </div>
    </div>
  );
}
