import { ActivityTimeline } from './ActivityTimeline';
import { DayHeader } from './DayHeader';
import { HotelCard } from './HotelCard';
import { PlaceCard } from './PlaceCard';
import { QuickStats } from './QuickStats';
import type { TripDay } from '../../entities/trip';
import { TripRouteBlock } from '../trip-route-block';
import styles from './TripDayCard.module.scss';

interface TripDayCardProps {
  day: TripDay;
}

export function TripDayCard({ day }: TripDayCardProps) {
  const recommendedPlaces = day.recommended_places ?? [];

  return (
    <article className={styles.card}>
      {day.route_from_previous && (
        <div className={styles.routeEntry}>
          <TripRouteBlock route={day.route_from_previous} />
        </div>
      )}

      <DayHeader
        dayNumber={day.day}
        title={day.title}
        city={day.city}
        location={day.location}
        heroImage={day.images?.hero}
      />

      <div className={styles.body}>
        <QuickStats day={day} />

        <div className={styles.storyGrid}>
          <ActivityTimeline activities={day.activities} />
          {day.hotel && <HotelCard hotel={day.hotel} />}
        </div>

        {recommendedPlaces.length > 0 && (
          <section className={styles.section}>
            <div className={styles.sectionHeader}>
              <div>
                <p className={styles.sectionEyebrow}>Along the way</p>
                <h4 className={styles.sectionTitle}>Places worth stopping for</h4>
              </div>
            </div>
            <div className={styles.placesCarousel}>
              {recommendedPlaces.map((place) => (
                <PlaceCard key={place.id} place={place} />
              ))}
            </div>
          </section>
        )}
      </div>
    </article>
  );
}
