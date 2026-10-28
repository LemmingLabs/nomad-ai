import { expect, test } from 'vitest';

import { formatDuration, formatEstimatedCost, getDisplayPlaceTypes, isRouteAvailable } from '../../entities/trip/lib/presentation.ts';

void test('shows hours and minutes for a multi-hour route', () => {
  expect(formatDuration(135)).toBe('2h 15m');
});

void test('only formats route cost when the estimate belongs to a taxi leg', () => {
  expect(formatEstimatedCost(3000, 'taxi')).toBe('~3,000 KGS');
  expect(formatEstimatedCost(0, 'driving')).toBeNull();
  expect(formatEstimatedCost(3000, 'walking')).toBeNull();
});

void test('hides unavailable routes', () => {
  expect(isRouteAvailable(null)).toBe(false);
  expect(isRouteAvailable({
    origin: 'A', destination: 'B', transport_type: 'unknown', distance_km: 0, duration_mins: 0,
  })).toBe(false);
  expect(isRouteAvailable({
    origin: 'A', destination: 'B', transport_type: 'taxi', distance_km: 15, duration_mins: 25,
  })).toBe(true);
});

void test('deduplicates and filters generic place types', () => {
  expect(getDisplayPlaceTypes(['food', 'museum', 'museum', 'art_gallery'])).toEqual(['Museum', 'Art Gallery']);
});
