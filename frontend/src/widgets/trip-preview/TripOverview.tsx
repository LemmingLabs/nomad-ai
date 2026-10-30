import type { TripDay } from '../../entities/trip';
import styles from './TripOverview.module.scss';

function coordinates(day: TripDay): { lat: number; lng: number } | null {
  const { lat, lng } = day.place_candidate ?? {};
  if (day.place_resolution?.status === 'unresolved' || typeof lat !== 'number' || typeof lng !== 'number' ||
      !Number.isFinite(lat) || !Number.isFinite(lng) || Math.abs(lat) > 90 || Math.abs(lng) > 180) return null;
  return { lat, lng };
}

export function TripOverview({ days, routeStatus }: { days: TripDay[]; routeStatus?: 'available' | 'unavailable' }) {
  const locations = days.map(coordinates);
  const valid = locations.filter((point): point is { lat: number; lng: number } => point !== null);
  const groups = new Map<string, { point: { lat: number; lng: number }; days: number[] }>();
  locations.forEach((point, index) => {
    if (!point) return;
    const key = `${point.lat},${point.lng}`;
    const group = groups.get(key);
    if (group) group.days.push(days[index].day);
    else groups.set(key, { point, days: [days[index].day] });
  });
  const minLat = Math.min(...valid.map((point) => point.lat));
  const maxLat = Math.max(...valid.map((point) => point.lat));
  const minLng = Math.min(...valid.map((point) => point.lng));
  const maxLng = Math.max(...valid.map((point) => point.lng));
  const project = (point: { lat: number; lng: number }) => ({
    x: maxLng === minLng ? 300 : 40 + (point.lng - minLng) / (maxLng - minLng) * 520,
    y: maxLat === minLat ? 120 : 200 - (point.lat - minLat) / (maxLat - minLat) * 160,
  });

  return (
    <details className={styles.overview} data-print-hide="true">
      <summary>Explore the trip overview <span>{valid.length} of {days.length} locations available</span></summary>
      <div className={styles.content}>
        <p>Suggested locations; dashed connections are schematic, not verified routes. Locations may be out of date.</p>
        {valid.length ? (
          <svg className={styles.diagram} viewBox="0 0 600 240" aria-hidden="true">
            {locations.map((point, index) => {
              const previous = locations[index - 1];
              if (!point || !previous) return null;
              const a = project(previous); const b = project(point);
              return <line key={`line-${index}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} />;
            })}
            {[...groups.entries()].map(([key, { point, days: numbers }]) => {
              const { x, y } = project(point);
              return <g key={key}><circle cx={x} cy={y} r="13" /><text x={x} y={y} dy=".35em" textAnchor="middle">{numbers.length > 2 ? '•' : numbers.join(',')}</text></g>;
            })}
          </svg>
        ) : <p>No coordinates are available. The ordered day list remains available below.</p>}
        {routeStatus === 'unavailable' && <p>Route details are unavailable; the overview works without a route provider.</p>}
        <ol className={styles.list}>
          {days.map((day, index) => (
            <li key={`${day.day}-${index}`}>
              <a href={`#trip-day-${day.day}`}>Day {day.day}: {day.location || day.city || day.title}</a>
              <span>{locations[index] ? 'Suggested location · freshness unconfirmed' : 'Location coordinates unavailable'}</span>
              {index > 0 && (day.route_from_previous?.status === 'stale' || day.route_from_previous?.status === 'unavailable' || !day.route_from_previous) && (
                <span>Route from previous day {day.route_from_previous?.status ?? 'unavailable'}</span>
              )}
            </li>
          ))}
        </ol>
      </div>
    </details>
  );
}
