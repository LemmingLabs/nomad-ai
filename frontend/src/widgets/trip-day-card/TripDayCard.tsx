import type { TripDay } from '../../entities/trip';
import {
  formatDistance,
  formatDuration,
  formatEstimatedCost,
  humanizeToken,
  isRouteAvailable,
} from '../../entities/trip/lib/presentation';
import { ActivityTimeline } from './ActivityTimeline';
import { DayHero } from './DayHero';
import { PlaceCandidateCard } from './PlaceCandidateCard';
import { QuickFacts } from './QuickFacts';
import styles from './TripDayCard.module.scss';

interface TripDayCardProps {
  day: TripDay;
}

export function TripDayCard({ day }: TripDayCardProps) {
  const routeAvailable = isRouteAvailable(day.route_from_previous);
  const placeCandidate = day.place_candidate;
  const heroImage = day.images?.hero;
  const transportType = humanizeToken(day.route_from_previous?.transport_type);

  return (
    <article className={styles.card}>
      <DayHero day={day} />

      <div className={styles.body}>
        <QuickFacts day={day} />

        <div className={styles.contentGrid}>
          <ActivityTimeline activities={day.activities} />

          <div className={styles.sidebar}>
            <PlaceCandidateCard day={day} />

            <section className={styles.panel}>
              <div className={styles.panelHeader}>
                <p className={styles.panelEyebrow}>Route summary</p>
                <h4 className={styles.panelTitle}>
                  {routeAvailable ? 'Transfer snapshot' : 'Journey pacing'}
                </h4>
              </div>

              {routeAvailable ? (
                <>
                  <p className={styles.routeHeadline}>
                    {day.route_from_previous?.origin} →{' '}
                    {day.route_from_previous?.destination}
                  </p>
                  <div className={styles.routeMeta}>
                    {transportType && (
                      <span className={styles.routeChip}>{transportType}</span>
                    )}
                    {formatDistance(day.route_from_previous?.distance_km) && (
                      <span className={styles.routeChip}>
                        {formatDistance(day.route_from_previous?.distance_km)}
                      </span>
                    )}
                    {formatDuration(day.route_from_previous?.duration_mins) && (
                      <span className={styles.routeChip}>
                        {formatDuration(day.route_from_previous?.duration_mins)}
                      </span>
                    )}
                    {formatEstimatedCost(
                      day.route_from_previous?.estimated_cost,
                    ) && (
                      <span className={styles.routeChip}>
                        {formatEstimatedCost(
                          day.route_from_previous?.estimated_cost,
                        )}
                      </span>
                    )}
                  </div>
                </>
              ) : (
                <p className={styles.panelCopy}>
                  {day.day === 1
                    ? `The story opens in ${day.city}, with ${day.location} as the first anchor point.`
                    : 'Transfer data was returned without reliable route metrics, so this leg is shown as an approximate move between destinations.'}
                </p>
              )}
            </section>

            <section className={styles.panel}>
              <div className={styles.panelHeader}>
                <p className={styles.panelEyebrow}>Useful travel info</p>
                <h4 className={styles.panelTitle}>At a glance</h4>
              </div>

              <dl className={styles.infoList}>
                <div className={styles.infoItem}>
                  <dt>Destination</dt>
                  <dd>{day.location}</dd>
                </div>
                <div className={styles.infoItem}>
                  <dt>Base city</dt>
                  <dd>{day.city}</dd>
                </div>
                <div className={styles.infoItem}>
                  <dt>Planned moments</dt>
                  <dd>{day.activities.length} curated stops</dd>
                </div>
                <div className={styles.infoItem}>
                  <dt>Travel focus</dt>
                  <dd>
                    {humanizeToken(placeCandidate?.matched_interest) ??
                      'AI-curated blend'}
                  </dd>
                </div>
                {heroImage?.photographer && (
                  <div className={styles.infoItem}>
                    <dt>Visual note</dt>
                    <dd>Hero photo by {heroImage.photographer}</dd>
                  </div>
                )}
              </dl>
            </section>
          </div>
        </div>
      </div>
    </article>
  );
}
