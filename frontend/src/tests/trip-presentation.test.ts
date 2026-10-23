import assert from 'node:assert/strict';
import test from 'node:test';

import { formatDuration, getDisplayPlaceTypes, isRouteAvailable } from '../entities/trip/lib/presentation.ts';

void test('shows hours and minutes for a multi-hour route', () => {
  assert.equal(formatDuration(135), '2h 15m');
});

void test('hides unavailable routes', () => {
  assert.equal(isRouteAvailable(null), false);
  assert.equal(isRouteAvailable({
    origin: 'A', destination: 'B', transport_type: 'unknown', distance_km: 0, duration_mins: 0,
  }), false);
  assert.equal(isRouteAvailable({
    origin: 'A', destination: 'B', transport_type: 'taxi', distance_km: 15, duration_mins: 25,
  }), true);
});

void test('deduplicates and filters generic place types', () => {
  assert.deepEqual(getDisplayPlaceTypes(['food', 'museum', 'museum', 'art_gallery']), ['Museum', 'Art Gallery']);
});
