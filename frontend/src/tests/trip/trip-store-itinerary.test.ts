import { afterEach, expect, test } from 'vitest';
import { useTripStore, type Trip, type TripItinerary } from '../../entities/trip';

afterEach(() => useTripStore.getState().clearTrips());

test('updates only the targeted itinerary and preserves newer trip metadata', () => {
  const itinerary: TripItinerary = { days: [] };
  const trip: Trip = {
    id: 1, title: 'Renamed trip', days: 1, created_at: '', updated_at: '',
    budget: 'medium', interests: [], travel_style: 'relaxed', itinerary_json: itinerary,
  };
  useTripStore.getState().setTrips([trip, { ...trip, id: 2, title: 'Other trip' }]);
  const updated: TripItinerary = { days: [{ day: 1, title: 'Lake', city: 'Karakol', location: 'Lake', activities: [] }] };

  useTripStore.getState().updateTripItinerary(1, updated);
  const [first, second] = useTripStore.getState().trips as Trip[];
  expect(first.title).toBe('Renamed trip');
  expect(first.itinerary_json).toEqual(updated);
  expect(second.itinerary_json).toEqual(itinerary);
});
