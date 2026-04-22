import cn from 'classnames';
import type { ReactNode } from 'react';
import type { TripItinerary } from '../../entities/trip';
import { TripDayCard } from '../trip-day-card';
import { TripHeader } from '../trip-header';
import styles from './TripPreview.module.scss';

interface TripPreviewProps {
  itinerary: TripItinerary | null | undefined;
  tripTitle?: string;
  actions?: ReactNode;
}

export function TripPreview({
  itinerary,
  tripTitle,
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
        totalDays={itinerary.days.length}
        summary={itinerary.summary}
        travelStyle={itinerary.travel_style}
        interests={itinerary.interests}
        actions={actions}
      />
      <div className={styles.days}>
        {itinerary.days.map((day, index) => (
          <div
            key={day.day}
            className={cn(styles.dayTrack, {
              [styles['dayTrack--last']]: index === itinerary.days.length - 1,
            })}
          >
            <div className={styles.dayRail} aria-hidden='true'>
              <span className={styles.dayMarker}>{day.day}</span>
              {index < itinerary.days.length - 1 && (
                <span className={styles.dayConnector} />
              )}
            </div>
            <TripDayCard day={day} />
          </div>
        ))}
      </div>
    </div>
  );
}
