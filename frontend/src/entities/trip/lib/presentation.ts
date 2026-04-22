import type { TripRoute } from '../model/types';

const genericPlaceTypes = new Set([
  'establishment',
  'point_of_interest',
  'food',
  'store',
  'premise',
  'political',
]);

const businessStatusLabels: Record<string, string> = {
  OPERATIONAL: 'Operational',
  CLOSED_TEMPORARILY: 'Temporarily closed',
  CLOSED_PERMANENTLY: 'Permanently closed',
};

export function formatNumber(
  value: number,
  options?: Intl.NumberFormatOptions,
): string {
  return new Intl.NumberFormat('en-US', options).format(value);
}

export function formatCompactNumber(value?: number | null): string | null {
  if (value == null) {
    return null;
  }

  return formatNumber(value, {
    notation: 'compact',
    maximumFractionDigits: value >= 1000 ? 1 : 0,
  });
}

export function formatDistance(distanceKm?: number | null): string | null {
  if (distanceKm == null || distanceKm <= 0) {
    return null;
  }

  return `${formatNumber(distanceKm, {
    maximumFractionDigits: distanceKm >= 10 ? 0 : 1,
  })} km`;
}

export function formatDuration(durationMins?: number | null): string | null {
  if (durationMins == null || durationMins <= 0) {
    return null;
  }

  const hours = Math.floor(durationMins / 60);
  const minutes = durationMins % 60;

  if (hours > 0 && minutes > 0) {
    return `${hours}h ${minutes}m`;
  }

  if (hours > 0) {
    return `${hours}h`;
  }

  return `${minutes}m`;
}

export function formatEstimatedCost(cost?: number | null): string | null {
  if (cost == null) {
    return null;
  }

  return `~${formatNumber(cost, { maximumFractionDigits: 0 })} KGS`;
}

export function humanizeToken(value?: string | null): string | null {
  if (!value) {
    return null;
  }

  return value
    .trim()
    .replace(/[_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

export function formatBusinessStatus(status?: string | null): string | null {
  if (!status) {
    return null;
  }

  return businessStatusLabels[status] ?? humanizeToken(status);
}

export function formatTravelStyle(style?: string | null): string | null {
  return humanizeToken(style);
}

export function getDisplayPlaceTypes(
  types?: string[] | null,
  limit = 3,
): string[] {
  if (!types?.length) {
    return [];
  }

  return Array.from(
    new Set(
      types.filter((type) => type && !genericPlaceTypes.has(type)).map((type) => humanizeToken(type) ?? type),
    ),
  ).slice(0, limit);
}

export function isRouteAvailable(route?: TripRoute | null): boolean {
  if (!route) {
    return false;
  }

  return !(
    route.transport_type === 'unknown' ||
    (route.distance_km === 0 && route.duration_mins === 0)
  );
}
